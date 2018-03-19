#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <OneWire.h>
#include <DallasTemperature.h>

WiFiClient client;

IPAddress ip(192,168,0,146);
int pollIntervalSecs = 1;

// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 2
// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

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
  char ssid[] = "ASUS";
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

  String postData=topTempLine + "\r\n" + bottomTempLine;
  
  Serial.println("Starting connection to server...");
  
  if (client.connect(ip, 8086)) {
    Serial.println("Connected to server");

    Serial.println("POST /write?db=metrics HTTP/1.1");
    Serial.println("Host: 192.168.0.146:8086");
    Serial.println("Authorization: Basic bGVlOkhoZXk5aHVr");
    Serial.println("User-Agent: Arduino");
    Serial.println("Accept: */*");
    Serial.print("Content-Length: ");
    Serial.println(postData.length());
    Serial.println("Content-Type: application/x-www-form-urlencoded");
    Serial.println();
    Serial.println(postData);
    Serial.println();
    
    client.println("POST /write?db=metrics HTTP/1.1");
    client.println("Host: 192.168.0.146:8086");
    client.println("Authorization: Basic bGVlOkhoZXk5aHVr");
    client.println("User-Agent: Arduino");
    client.println("Accept: */*");
    client.print("Content-Length: ");
    client.println(postData.length());
    client.println("Content-Type: application/x-www-form-urlencoded");    
    client.println();
    client.println(postData);
    client.println();
    client.flush();
    client.stop();
    
    Serial.println("Sent metrics");
  }
 
  Serial.println();
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
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
