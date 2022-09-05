import logging

from influxdb_client import InfluxDBClient

INFLUXDB_SERVER_ADDRESS = 'INFLUXDB_SERVER_ADDRESS'
INFLUXDB_SERVER_PORT = 'INFLUXDB_SERVER_PORT'
INFLUXDB_AUTH_TOKEN = 'INFLUXDB_AUTH_TOKEN'
INFLUXDB_AUTH_ORG = 'INFLUXDB_AUTH_ORG'


class InfluxDBProvider:

    def __init__(self, options, auto_connect=True):
        self.log = logging.getLogger('InfluxDBProvider')
        self.options = options
        self.auto_connect = auto_connect
        if self.auto_connect:
            self.server_address = options[INFLUXDB_SERVER_ADDRESS]
            self.server_port = options[INFLUXDB_SERVER_PORT]
            influxdb_url = f'http://{self.server_address}:{self.server_port}'
            self.influxdb_client = InfluxDBClient(url=influxdb_url)

    def can_connect(self):
        return self.influxdb_client.ping()
