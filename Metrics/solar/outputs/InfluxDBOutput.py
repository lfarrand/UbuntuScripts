import PluginLoader
import datetime

class InfluxDBOutput(PluginLoader.Plugin):
    """Stores the data from the Omnik inverter into an InfluxDB database"""

    def process_message(self, msg):
        """Store the information from the inverter in an InfluxDB database.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """
        from influxdb import InfluxDBClient
        from datetime import datetime

        timenow = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        influxserver = self.config.get('influx', 'host')
        influxdb = self.config.get('influx', 'database')
        influxuser = self.config.get('influx', 'user')
        influxpass = self.config.get('influx', 'pass')
        influxport = self.config.get('influx', 'port')

        self.logger.debug('Connect to InfluxDB')

        json_body = [
            {
                "measurement": "solarpv",
                "tags": {
                    "inverter_id": msg.id
                },
                "time": timenow,
                "fields": {
                    "power_output": msg.power,
                    "temperature": msg.temperature,
                    "energy_total_kWh": msg.e_total,
                    "energy_today_kWh": msg.e_today,
                    "total_hours": msg.h_total,
                    "pv1_volts": msg.v_pv(1),
                    "pv1_amps": msg.i_pv(1),
                    "pv2_volts": msg.v_pv(2),
                    "pv2_amps": msg.i_pv(2),
                    "pv3_volts": msg.v_pv(3),
                    "pv3_amps": msg.i_pv(3),
                    "ac1_volts": msg.v_ac(1),
                    "ac1_amps": msg.i_ac(1),
                    "ac1_hertz": msg.f_ac(1),
                    "ac1_watts": msg.p_ac(1),
                    "ac2_volts": msg.v_ac(2),
                    "ac2_amps": msg.i_ac(2),
                    "ac2_hertz": msg.f_ac(2),
                    "ac2_watts": msg.p_ac(2),
                    "ac3_volts": msg.v_ac(3),
                    "ac3_amps": msg.i_ac(3),
                    "ac3_hertz": msg.f_ac(3),
                    "ac3_watts": msg.p_ac(3)
                }
            }
        ]

        # print(json_body)

        client = InfluxDBClient(influxserver, influxport, influxuser, influxpass, influxdb)
        client.write_points(json_body)
