import logging
from datetime import datetime, timedelta

from coreutility.date.NanoTimestamp import NanoTimestamp
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from timeseries.provider.point.PointBuilder import build_point

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
            self.write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

    def can_connect(self):
        return self.influxdb_client.ping()

    def add_to_timeseries(self, measurement, instrument, price, time=None):
        with self.influxdb_client.write_api() as write_client:
            point = Point(measurement).tag("instrument", instrument).field("price", price)
            if time is not None:
                point.time(time, write_precision=WritePrecision.NS)
            write_client.write(bucket=self.bucket, record=point)

    def batch_add_to_timeseries(self, measurement, data):
        points = [build_point(measurement, d[0], d[1], d[2] if len(d) > 2 else None) for d in data]
        with self.influxdb_client.write_api() as write_client:
            write_client.write(bucket=self.bucket, record=points)

    def get_timeseries_data(self, measurement, instrument):
        # todo: refine
        print('getting timeseries data...')
        query = f'from(bucket: "{self.bucket}")' \
                ' |> range(start: -30d, stop: now())' \
                f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")' \
                f' |> filter(fn: (r) => r["instrument"] == "{instrument}")' \
                ' |> filter(fn: (r) => r["_field"] == "price")'
        tables = self.influxdb_client.query_api().query(query, org=self.auth_org)
        results = []
        for table in tables:
            for record in table.records:
                results.append((NanoTimestamp.as_nanoseconds(record["_time"]), record["_value"]))
        return results

    def delete_timeseries(self, measurement):
        # todo: refine
        time_now = datetime.now()
        # influx 'default' timestamps can slightly be in the future (see _stop which is 10s faster)
        # also, delete does not use nano (full) seconds! (use datetime) [delete of influx is different & needs to be consistent]
        time_now_future = time_now + timedelta(hours=1)
        time_in_past = time_now - timedelta(days=30)
        end_time = time_now_future
        start_time = time_in_past
        self.delete_api.delete(start_time, end_time, f'_measurement="{measurement}"', bucket=self.bucket, org=self.auth_org)
