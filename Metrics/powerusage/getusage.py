from influxdb import InfluxDBClient
import socket
import argparse
import json
from datetime import datetime
import time

version = 1.0
powerPlugAddresses = [
    ['Garage', '192.168.0.215'],
    ['Tumble Dryer', '192.168.0.244'],
    ['TV', '192.168.0.122'],
    ['Study', '192.168.0.140'],
    ['Dishwasher', '192.168.0.189'],
    ['Washing Machine', '192.168.0.172'],
    ['Under Stairs Cupboard', '192.168.0.177'],
    ['Quooker Tap', '192.168.0.247'],
    ['Fridge', '192.168.0.119'],
    ['Miner', '192.168.0.102']
]

parser = argparse.ArgumentParser(description="TP-Link Wi-Fi Smart Plug Monitoring Client v" + str(version))
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


# Check if IP is valid
def validIP(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error:
        parser.error("Invalid IP Address.")
    return ip


# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
commands = {'info': '{"system":{"get_sysinfo":{}}}',
            'on': '{"system":{"set_relay_state":{"state":1}}}',
            'off': '{"system":{"set_relay_state":{"state":0}}}',
            'cloudinfo': '{"cnCloud":{"get_info":{}}}',
            'wlanscan': '{"netif":{"get_scaninfo":{"refresh":0}}}',
            'time': '{"time":{"get_time":{}}}',
            'schedule': '{"schedule":{"get_rules":{}}}',
            'countdown': '{"count_down":{"get_rules":{}}}',
            'antitheft': '{"anti_theft":{"get_rules":{}}}',
            'reboot': '{"system":{"reboot":{"delay":1}}}',
            'reset': '{"system":{"reset":{"delay":1}}}'
            }


# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
    key = 171
    result = "\0\0\0\0"
    for i in string:
        a = key ^ ord(i)
        key = a
        result += chr(a)
    return result


def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ ord(i)
        key = ord(i)
        result += chr(a)
    return result


def query(ip, port, querycmd):
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.settimeout(10.0)
    sock_tcp.connect((ip, port))
    sock_tcp.send(encrypt(querycmd))
    data = sock_tcp.recv(2048)
    queryresult = decrypt(data[4:])
    sock_tcp.close()

    del sock_tcp
    del data

    # print "Sent:     ", querycmd
    # print "Received: ", queryresult
    return queryresult


def gatherStatsAndPost(ip, port, timenow):
    try:
        print 'Getting usage for {}:{}'.format(ip, port)
        sysinforesult = query(ip, port, '{"system":{"get_sysinfo":{}}}')
        sysinfojson = json.loads(sysinforesult)
        alias = sysinfojson['system']['get_sysinfo']['alias']

        print 'Got usage for {}:{} ({})'.format(ip, port, alias)

        usageresult = query(ip, port, '{"emeter":{"get_realtime":{}}}')
        usagejson = json.loads(usageresult)
        amps = float(usagejson['emeter']['get_realtime']['current'])
        volts = float(usagejson['emeter']['get_realtime']['voltage'])
        watts = float(usagejson['emeter']['get_realtime']['power'])
        total = float(usagejson['emeter']['get_realtime']['total'])

        # timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        today = datetime.today()

        historicusageresult = query(ip, port, '{"emeter": {"get_daystat": {"month": ' + str(today.month) + ', "year": ' + str(today.year) + '}}}')
        historicusagejson = json.loads(historicusageresult)
        historiccount = int(len(historicusagejson['emeter']['get_daystat']['day_list']))
        totaltoday = float(historicusagejson['emeter']['get_daystat']['day_list'][historiccount-1]['energy'])

        historicjson_body = [
            {
                "measurement": "energy",
                "tags": {
                    "alias": alias
                },
                "time": timenow,
                "fields": {
                    "kWh": totaltoday
                }
            }
        ]

        json_body = [
            {
                "measurement": "power_usage",
                "tags": {
                    "alias": alias
                },
                "time": timenow,
                "fields": {
                    "amps": amps,
                    "volts": volts,
                    "watts": watts,
                    "total": total
                }
            }
        ]

        client = InfluxDBClient(influxserver, 8086, influxuser, influxpass, influxdb)

        print 'Sending instant power usage for {} to influx {}:{}'.format(alias, influxserver, 8086)
        client.write_points(json_body)

        print 'Sending historic power usage for {} to influx'.format(alias)
        client.write_points(historicjson_body)

        del usagejson
        del usageresult
        del sysinfojson
        del sysinforesult
        del json_body
        del historicjson_body
        del client

    except socket.error, v:
        print 'Skipping {}:{} due to error: {}'.format(ip, port, v.message)


def printError(failure):
    print(str(failure))


while True:
    timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print 'Checking power usage at {}'.format(timenow)
    for powerPlugAddress in powerPlugAddresses:
        gatherStatsAndPost(powerPlugAddress[1], port, timenow)
    print 'Finished checking power usage'
    time.sleep(10)
