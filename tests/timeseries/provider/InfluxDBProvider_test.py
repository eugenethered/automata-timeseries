import logging
import unittest

from timeseries.provider.InfluxDBProvider import InfluxDBProvider


class InfluxDBProviderTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('RedisCacheProvider').setLevel(logging.DEBUG)

        self.options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1',
            'INFLUXDB_SERVER_PORT': 8086
        }

    def test_should_connect_to_influxdb_server(self):
        timeseries_provider = InfluxDBProvider(self.options)
        connected = timeseries_provider.can_connect()
        self.assertEqual(connected, True)


if __name__ == '__main__':
    unittest.main()
