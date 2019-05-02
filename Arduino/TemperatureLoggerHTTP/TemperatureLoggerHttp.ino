#include <SPI.h>
#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoHttpClient.h>

char serverAddress[] = "192.168.123.90";
int port = 8086;
WiFiClient wifiClient;
HttpClient httpClient = HttpClient(wifiClient, serverAddress, port);
String response;
int statusCode = 0;
String authData = "Basic bGVlOkhoZXk5aHVr";
int pollIntervalSecs = 10;

// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  uint8_t devCnt = sensors.getDeviceCount();
  bool a = sensors.isParasitePowerMode();

  Serial.println("Num devices: " + devCnt);
  Serial.println("Parasite power?: " + a);

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv != "1.1.0") {
    Serial.println("Please upgrade the firmware");
  }
}

void loop() {
  connectWifi();

  sensors.requestTemperatures();

  logTemperature();
  
  delay(pollIntervalSecs * 1000);
}

void connectWifi() {
  char ssid[] = "Wrt32x-2.4G";
  char pass[] = "hhey9huk";
  int keyIndex = 0;

  int status = WiFi.status();

  if(status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);

    while (status != WL_CONNECTED) {
      status = WiFi.begin(ssid, pass);
      delay ( 500 );
      Serial.print ( "." );
    }
    
    Serial.println("Connected to WiFi");
    printWifiStatus();
  }
  else {
    Serial.print("Connected to SSID: ");
    Serial.println(ssid);
  }
}

void logTemperature() {
  String topTempLine,bottomTempLine;

  float topTemp = sensors.getTempCByIndex(0);
  float bottomTemp = sensors.getTempCByIndex(1);
  
  topTempLine = String("hotwater,location=top temperature=" + String(topTemp, 2));
  bottomTempLine = String("hotwater,location=bottom temperature=" + String(bottomTemp, 2));

  String postData=topTempLine + "\n" + bottomTempLine;
  
  Serial.println("Starting connection to server...");

  httpPost("/write?db=metrics", "application/x-www-form-urlencoded", postData);
 
  Serial.println();
}

void httpPost( String path, String contentType, String postData)
{
  Serial.println("Making POST request");
  Serial.println("Post data: ");
  Serial.println(postData);

  httpClient.beginRequest();
  httpClient.post(path);
  httpClient.sendHeader("Authorization", authData);
  httpClient.sendHeader("Content-Type", contentType);
  httpClient.sendHeader("Content-Length", postData.length());
  httpClient.endRequest();
  httpClient.print(postData);

  statusCode = httpClient.responseStatusCode();
  response = httpClient.responseBody();

  httpClient.flush();
  httpClient.stop();

  Serial.print("Status code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
