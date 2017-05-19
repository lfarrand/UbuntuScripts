from influxdb import InfluxDBClient
import argparse
from datetime import datetime
import nest

version = 0.1
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

napi = nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file)

if napi.authorization_required:
    print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
    pin = input("PIN: ")
    napi.request_token(pin)

timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

for structure in napi.structures:
    for device in structure.thermostats:
        json_body = [
            {
                "measurement": "temp_humidity",
                "tags": {
                    "device": device.name,
                    "where": device.where
                },
                "time": timenow,
                "fields": {
                    "temperature": device.temperature,
                    "humidity": device.humidity
                }
            }
        ]

        client = InfluxDBClient(influxserver, 8086, influxuser, influxpass, influxdb)
        client.write_points(json_body)
