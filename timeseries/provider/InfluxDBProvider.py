import logging
from datetime import datetime, timedelta

from coreutility.date_utility import as_nano_second_timestamp
from influxdb_client import InfluxDBClient, Point

INFLUXDB_SERVER_ADDRESS = 'INFLUXDB_SERVER_ADDRESS'
INFLUXDB_SERVER_PORT = 'INFLUXDB_SERVER_PORT'
INFLUXDB_AUTH_TOKEN = 'INFLUXDB_AUTH_TOKEN'
INFLUXDB_AUTH_ORG = 'INFLUXDB_AUTH_ORG'
INFLUXDB_BUCKET = 'INFLUXDB_BUCKET'


class InfluxDBProvider:

    def __init__(self, options, auto_connect=True):
        self.log = logging.getLogger('InfluxDBProvider')
        self.options = options
        self.auto_connect = auto_connect
        if self.auto_connect:
            self.server_address = options[INFLUXDB_SERVER_ADDRESS]
            self.server_port = options[INFLUXDB_SERVER_PORT]
            self.auth_token = options[INFLUXDB_AUTH_TOKEN]
            self.auth_org = options[INFLUXDB_AUTH_ORG]
            self.bucket = options[INFLUXDB_BUCKET]
            influxdb_url = f'http://{self.server_address}:{self.server_port}'
            self.influxdb_client = InfluxDBClient(url=influxdb_url, token=self.auth_token, org=self.auth_org)
            self.query_api = self.influxdb_client.query_api()
            self.delete_api = self.influxdb_client.delete_api()

    def can_connect(self):
        return self.influxdb_client.ping()

    def add_to_timeseries(self, measurement, instrument, price, time=None):
        with self.influxdb_client.write_api() as write_client:
            point = Point(measurement).tag("instrument", instrument).field("price", price)
            if time is not None:
                point.time(time)
            write_client.write(bucket=self.bucket, record=point)
        print(f'writing for time[{time}] {instrument} {price}')

    def get_timeseries_data(self, measurement, instrument):
        query = f'from(bucket: "{self.bucket}")' \
                ' |> range(start: -1h, stop: now())' \
                f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")' \
                f' |> filter(fn: (r) => r["instrument"] == "{instrument}")' \
                ' |> filter(fn: (r) => r["_field"] == "price")'
        tables = self.influxdb_client.query_api().query(query, org=self.auth_org)
        results = []
        for table in tables:
            for record in table.records:
                print(f'data -> [{as_nano_second_timestamp(record["_time"])}] {record["_time"]} {record["_value"]}')
                results.append((as_nano_second_timestamp(record["_time"]), record["_value"]))
        return results

    def delete_timeseries(self, measurement):
        time_now = datetime.now()
        # influx 'default' timestamps can slightly be in the future (see _stop which is 10s faster)
        time_now_future = time_now + timedelta(hours=1)
        time_in_past = time_now - timedelta(days=30)
        end_time = as_nano_second_timestamp(time_now_future)
        start_time = as_nano_second_timestamp(time_in_past)
        self.delete_api.delete(start_time, end_time, f'_measurement="{measurement}"', bucket=self.bucket, org=self.auth_org)
