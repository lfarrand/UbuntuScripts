import sys
from influxdb import InfluxDBClient
import argparse
import json
import requests
from datetime import datetime
import time

version = 1.0
remoteServerAddresses = [
    ['Miner', '192.168.0.245']
]

parser = argparse.ArgumentParser(description="Hardware Stats Poller v" + str(version))
parser.add_argument("-is", "--influxserver", metavar="<influxserver>", required=True, help="Influx Server")
parser.add_argument("-idb", "--influxdb", metavar="<influxdb>", required=True, help="Influx Database")
parser.add_argument("-iusr", "--influxuser", metavar="<influxuser>", required=True, help="Influx Username")
parser.add_argument("-ipass", "--influxpass", metavar="<influxpass>", required=True, help="Influx Password")
args = parser.parse_args()

influxserver = args.influxserver
influxdb = args.influxdb
influxuser = args.influxuser
influxpass = args.influxpass
port = 55555


def gatherStatsAndPost(host, ip, port):
    try:
        response = requests.get("http://{}:{}".format(ip, port))

        jsonObject = json.loads(response.content)

        json_body = []

        for dict in jsonObject:
            json_body.append({
                "measurement": "{}".format(dict["SensorName"]),
                "tags": {
                    "host": host,
                    "alias": "{}".format(dict["SensorClass"].strip(": "))
                },
                "time": long("{}".format(dict["SensorUpdateTime"])) * 1000000000,
                "fields": {
                    "value": float("{}".format(dict["SensorValue"])),
                    "unit": "{}".format(dict["SensorUnit"].encode('utf-8'))
                }
            })

        print json.dumps(json_body)

        client = InfluxDBClient(influxserver, 8086, influxuser, influxpass, influxdb)
        client.write_points(json_body)

        del json_body
        del jsonObject
        del response
        del client

    except requests.exceptions.RequestException as e:
        print 'Skipping {}:{} due to error \'{}\''.format(ip, port, e.strerror, e.message)
    except:
        e = sys.exc_info()[0]
        print 'Skipping {}:{} due to error \'{}\''.format(ip, port, e.strerror, e.message)


def printError(failure):
    print(str(failure))


while True:
    timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for address in remoteServerAddresses:
        print 'Getting hardware stats for {} at {}'.format(address[0], timenow)
        gatherStatsAndPost(address[0], address[1], port)

    print 'Finished checking hardware stats'
    time.sleep(10)
