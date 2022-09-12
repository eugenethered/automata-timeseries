import logging
from datetime import datetime, timedelta

from core.number.BigFloat import BigFloat
from core.options.exception.MissingOptionError import MissingOptionError
from coreutility.date.NanoTimestamp import NanoTimestamp
from influxdb_client import InfluxDBClient

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
        self.__check_options()
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

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {INFLUXDB_SERVER_ADDRESS} and {INFLUXDB_SERVER_PORT}')
            raise MissingOptionError(f'missing option please provide options {INFLUXDB_SERVER_ADDRESS} and {INFLUXDB_SERVER_PORT}')
        if self.auto_connect is True:
            if INFLUXDB_SERVER_ADDRESS not in self.options:
                self.log.warning(f'missing option please provide option {INFLUXDB_SERVER_ADDRESS}')
                raise MissingOptionError(f'missing option please provide option {INFLUXDB_SERVER_ADDRESS}')
            if INFLUXDB_SERVER_PORT not in self.options:
                self.log.warning(f'missing option please provide option {INFLUXDB_SERVER_PORT}')
                raise MissingOptionError(f'missing option please provide option {INFLUXDB_SERVER_PORT}')

    def can_connect(self):
        return self.influxdb_client.ping()

    def add_to_timeseries(self, measurement, instrument, price: BigFloat, time=None):
        with self.influxdb_client.write_api() as write_client:
            point = build_point(measurement, instrument, price, time)
            write_client.write(bucket=self.bucket, record=point)

    def batch_add_to_timeseries(self, measurement, data):
        points = [build_point(measurement, d[0], d[1], d[2] if len(d) > 2 else None) for d in data]
        with self.influxdb_client.write_api() as write_client:
            write_client.write(bucket=self.bucket, record=points)

    def get_timeseries_data(self, measurement, instrument, range_from='-30d', range_to='now()'):
        query = f'from(bucket: "{self.bucket}")' \
                f' |> range(start: {range_from}, stop: {range_to})' \
                f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")' \
                f' |> filter(fn: (r) => r["instrument"] == "{instrument}")' \
                ' |> filter(fn: (r) => r["_field"] == "price")' \
                ' |> sort(columns: ["_time"], desc: true)'
        tables = self.influxdb_client.query_api().query(query, org=self.auth_org)
        results = []
        for table in tables:
            for record in table.records:
                results.append((NanoTimestamp.as_nanoseconds(record["_time"]), BigFloat(str(record["_value"]))))
        return results

    def delete_timeseries(self, measurement, range_from='-30d', range_to='now()'):
        time_now = datetime.now()
        # influx 'default' timestamps can slightly be in the future (see _stop which is 10s faster)
        # also, delete does not use nano (full) seconds! (use datetime) [delete of influx is different & needs to be consistent]
        time_now_future = time_now + timedelta(minutes=1) if range_to == 'now()' else time_now + timedelta(minutes=int(range_to))
        range_from_normalize = int(range_from.replace('d', '').replace('-', ''))
        time_in_past = time_now - timedelta(days=range_from_normalize)
        end_time = time_now_future
        start_time = time_in_past
        self.delete_api.delete(start_time, end_time, f'_measurement="{measurement}"', bucket=self.bucket, org=self.auth_org)
