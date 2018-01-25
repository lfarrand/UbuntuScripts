from nicehashconfig import *

try:

    import json
    import time
    import logging
    import logging.handlers
    from datetime import datetime
    from influxdb import InfluxDBClient
    import argparse

    LEVEL = logging.DEBUG  # Pick minimum level of reporting logging - debug OR info

    # Format to include when, who, where, what
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Name is module name
    logger = logging.getLogger(__name__)
    logger.setLevel(LEVEL)

    if __name__ == "__main__":
        logging.info("Begin")

    # Create file size limit and file name
    handler = logging.handlers.RotatingFileHandler('debug.log', maxBytes=2000000, backupCount=10)
    handler.setLevel(LEVEL)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    logger.debug("Starting app")

    version = 0.1

    parser = argparse.ArgumentParser(description="Nicehash Stats Poller v" + str(version))
    parser.add_argument("-is", "--influxserver", metavar="<influxserver>", required=True, help="Influx Server")
    parser.add_argument("-idb", "--influxdb", metavar="<influxdb>", required=True, help="Influx Database")
    parser.add_argument("-iusr", "--influxuser", metavar="<influxuser>", required=True, help="Influx Username")
    parser.add_argument("-ipass", "--influxpass", metavar="<influxpass>", required=True, help="Influx Password")
    args = parser.parse_args()

    influxserver = args.influxserver
    influxdb = args.influxdb
    influxuser = args.influxuser
    influxpass = args.influxpass

    def queryStats():
        import json, requests

        url = 'https://api.nicehash.com/api'

        params = dict(
            method='stats.provider.ex',
            addr=btcAddress
        )

        resp = requests.get(url=url, params=params)
        stats = json.loads(resp.text)

        # print json.dumps(stats)
        return stats


    def getProf(stats):
        # print (stats["result"]["current"])
        totalProf = 0
        for i in stats["result"]["current"]:
            algoProf = float(i["profitability"])

            if "a" in i["data"][0]:
                # there is activity for this algo
                # to get the profitability per day in BTC, multiply "a" rate by algo profitability and add to total prof
                totalProf = totalProf + algoProf * float(i["data"][0]["a"])
        logger.debug("current total profitability in BTC/day is " + str(totalProf))
        return totalProf


    def getProfByAlgo(stats):

        profitabilityByAlgo = {}

        # print (stats["result"]["current"])
        for i in stats["result"]["current"]:
            algoProf = float(i["profitability"])

            if "a" in i["data"][0]:
                # there is activity for this algo
                # to get the profitability per day in BTC, multiply "a" rate by algo profitability and add to total prof
                algoProf = algoProf * float(i["data"][0]["a"])
                profitabilityByAlgo[i['name']] = {'name': i['name'], 'profitability': algoProf}
            else:
                profitabilityByAlgo[i['name']] = ({'name': i['name'], 'profitability': float(0)})
        return profitabilityByAlgo

    statsNow = queryStats()

    timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    totalProfitability = getProf(statsNow)
    algoProf = getProfByAlgo(statsNow)

    # print json.dumps(algoProf)

    json_body = [
        {
            "measurement": "NiceHashProfitability",
            "tags": {
                "BtcAddress": btcAddress
            },
            "time": timenow,
            "fields": {
                "TotalProfitability": totalProfitability
            }
        }
    ]

    for key, value in algoProf.items():
        json_body[0]['fields'][key] = value['profitability']

    logger.debug(json.dumps(json_body))

    client = InfluxDBClient(influxserver, 8086, influxuser, influxpass, influxdb)
    client.write_points(json_body)

    logger.debug("Posted stats to InfluxDB")

except Exception as e:
    logger.exception("Something bad happened. Error: {}".format(e.message))
