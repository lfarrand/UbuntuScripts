import json

def main():

    # create a simple JSON array
    jsonString = """[
    {
        "SensorApp": "HWiNFO",
        "SensorClass": "GPU [#6]: NVIDIA GeForce GTX 1070 Ti: ",
        "SensorName": "GPU Power",
        "SensorValue": "144.396",
        "SensorUnit": "W",
        "SensorUpdateTime": 1516792311
    },
    {
        "SensorApp": "HWiNFO",
        "SensorClass": "GPU [#6]: NVIDIA GeForce GTX 1070 Ti: ",
        "SensorName": "GPU Clock",
        "SensorValue": "1873",
        "SensorUnit": "MHz",
        "SensorUpdateTime": 1516792311
    },
    {
        "SensorApp": "HWiNFO",
        "SensorClass": "GPU [#6]: NVIDIA GeForce GTX 1070 Ti: ",
        "SensorName": "GPU Memory Clock",
        "SensorValue": "2079",
        "SensorUnit": "MHz",
        "SensorUpdateTime": 1516792311
    }]"""

    json_body = []

    # change the JSON string into a JSON object
    jsonObject = json.loads(jsonString)

    a = {}
    a['1'] = 1

    # print the keys and values
    for dict in jsonObject:
        json_body.append({
            "measurement": "{}".format(dict["SensorName"]),
            "tags": {
                "host": "miner",
                "alias": "{}".format(dict["SensorClass"].strip(": "))
            },
            "time": int("{}".format(dict["SensorUpdateTime"])),
            "fields": {
                "value": float("{}".format(dict["SensorValue"])),
                "unit": "{}".format(dict["SensorUnit"])
            }
        })

            #a[deviceName].append("{}{}".format(key, value))
            # print("{}: {}".format(key, value))

    print json.dumps(json_body)

    pass

if __name__ == '__main__':
    main()