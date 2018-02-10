from influxdb import InfluxDBClient
import argparse
from datetime import datetime
import nest
import time

version = 1.0
parser = argparse.ArgumentParser(description="Nest Monitoring Client v" + str(version))
parser.add_argument("-is", "--influxserver", metavar="<influxserver>", required=True, help="Influx Server")
parser.add_argument("-idb", "--influxdb", metavar="<influxdb>", required=True, help="Influx Database")
parser.add_argument("-iusr", "--influxuser", metavar="<influxuser>", required=True, help="Influx Username")
parser.add_argument("-ipass", "--influxpass", metavar="<influxpass>", required=True, help="Influx Password")
args = parser.parse_args()

influxserver = args.influxserver
influxdb = args.influxdb
influxuser = args.influxuser
influxpass = args.influxpass
port = 9999

client_id = '00d70f3d-fb03-4fbe-aaae-c79fe4a61421'
client_secret = 'xsnjpiP7mEElGEbb72eRWsn3N'
access_token_cache_file = 'nest.json'

while True:
    timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print 'Getting Nest stats at {}'.format(timenow)

    napi = nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file)

    if napi.authorization_required:
        print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
        pin = input("PIN: ")
        napi.request_token(pin)

    for structure in napi.structures:
        for device in structure.thermostats:

            isHeating = 0
            if device.hvac_state == "heating":
                isHeating = 1

            json_body = [
                {
                    "measurement": "temp_humidity",
                    "tags": {
                        "device": device.name,
                        "where": device.where,
                        "mode": device.mode
                    },
                    "time": timenow,
                    "fields": {
                        "temperature": device.temperature,
                        "humidity": device.humidity,
                        "heating": isHeating
                    }
                }
            ]

            # print(json_body)

            client = InfluxDBClient(influxserver, 8086, influxuser, influxpass, influxdb)

            print '{} temperature is {} and humidity is {}'.format(device.name, device.temperature, device.humidity)
            print 'Sending Nest stats for {} to influx {}:{}'.format(device.name, influxserver, 8086)
            client.write_points(json_body)

            del client
            del json_body

    del napi

    print 'Finished checking Nest stats'
    time.sleep(10)
