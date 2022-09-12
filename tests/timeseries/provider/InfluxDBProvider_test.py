import logging
import unittest

from core.number.BigFloat import BigFloat
from coreutility.date.NanoTimestamp import NanoTimestamp

from timeseries.provider.InfluxDBProvider import InfluxDBProvider


class InfluxDBProviderTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('InfluxDBProvider').setLevel(logging.DEBUG)

        self.options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1',
            'INFLUXDB_SERVER_PORT': 8086,
            'INFLUXDB_AUTH_TOKEN': 'q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==',
            'INFLUXDB_AUTH_ORG': 'persuader-technology',
            'INFLUXDB_BUCKET': 'automata'
        }

    def tearDown(self):
        timeseries_provider = InfluxDBProvider(self.options)
        timeseries_provider.delete_timeseries('timeseries-test')

    def test_should_connect_to_influxdb_server(self):
        timeseries_provider = InfluxDBProvider(self.options)
        connected = timeseries_provider.can_connect()
        self.assertEqual(connected, True)

    def test_should_obtain_timeseries_points(self):
        # using write-multiple-timeseries-points.sh (CURL api simulation)
        timeseries_provider = InfluxDBProvider(self.options)
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        self.assertEqual(len(timeseries_data), 6, 'Run write-multiple-timeseries-points.sh 1st! (in simulations/api)')

    def test_should_store_time_series_point_with_autogenerated_date(self):
        timeseries_provider = InfluxDBProvider(self.options)
        timeseries_provider.add_to_timeseries('timeseries-test', 'test', BigFloat('1.00'))
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        (point_timestamp, point_value) = timeseries_data[0]
        self.assertRegex(point_timestamp.__str__(), r'^\d{19}$')
        self.assertEqual(point_value, BigFloat('1.00'))

    def test_should_store_time_series_point_with_specified_date(self):
        timeseries_provider = InfluxDBProvider(self.options)
        supplied_time = NanoTimestamp.get_nanoseconds()
        timeseries_provider.add_to_timeseries('timeseries-test', 'test', BigFloat('2.00'), supplied_time)
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        (point_timestamp, point_value) = timeseries_data[0]
        # although full nano supplied, results come back as nano-ish!
        self.assertEqual(point_timestamp - (point_timestamp % 1000), supplied_time - (supplied_time % 1000))
        self.assertEqual(point_value, BigFloat('2.00'))

    def test_should_store_time_series_point_but_override_specified_date_when_not_full_nano(self):
        timeseries_provider = InfluxDBProvider(self.options)
        supplied_time = 1648913430060
        timeseries_provider.add_to_timeseries('timeseries-test', 'test', BigFloat('115.16'), supplied_time)
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        (point_timestamp, point_value) = timeseries_data[0]
        self.assertRegex(point_timestamp.__str__(), r'^\d{19}$', 'should override non-nano time')
        self.assertEqual(point_value, BigFloat('115.16'))

    def test_should_store_multiple_time_series_points_without_specifying_time(self):
        timeseries_provider = InfluxDBProvider(self.options)
        data = [
            ('test', BigFloat('10.00')),
            ('test', BigFloat('11.00')),
            ('test', BigFloat('12.00'))
        ]
        timeseries_provider.batch_add_to_timeseries('timeseries-test', data)
        # will always return in descending order (latest 1st)
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        expected = [BigFloat('12.0'), BigFloat('11.0'), BigFloat('10.0')]
        self.assertRegex(timeseries_data[0][0].__str__(), r'^\d{19}$')
        self.assertEqual(expected[0], timeseries_data[0][1])
        self.assertRegex(timeseries_data[1][0].__str__(), r'^\d{19}$')
        self.assertEqual(expected[1], timeseries_data[1][1])
        self.assertRegex(timeseries_data[2][0].__str__(), r'^\d{19}$')
        self.assertEqual(expected[2], timeseries_data[2][1])

    def test_should_store_multiple_time_series_points_with_specifying_time(self):
        timeseries_provider = InfluxDBProvider(self.options)
        data = [
            ('test', BigFloat('1.00'), NanoTimestamp.get_nanoseconds()),
            ('test', BigFloat('0.000000000012'), NanoTimestamp.get_nanoseconds()),
            ('test', BigFloat('123456789012.123456789012'), NanoTimestamp.get_nanoseconds())
        ]
        timeseries_provider.batch_add_to_timeseries('timeseries-test', data)
        timeseries_data = timeseries_provider.get_timeseries_data('timeseries-test', 'test')
        # although full nano supplied, results come back as nano-ish! times are from original ;)
        expected = [
            (data[2][2] - (data[2][2] % 1000), BigFloat('123456789012.123456789012')),
            (data[1][2] - (data[1][2] % 1000), BigFloat('0.000000000012')),
            (data[0][2] - (data[0][2] % 1000), BigFloat('1.0'))
        ]
        self.assertEqual(expected[0][0], timeseries_data[0][0])
        self.assertEqual(expected[0][1], timeseries_data[0][1])
        self.assertEqual(expected[1][0], timeseries_data[1][0])
        self.assertEqual(expected[1][1], timeseries_data[1][1])
        self.assertEqual(expected[2][0], timeseries_data[2][0])
        self.assertEqual(expected[2][1], timeseries_data[2][1])


if __name__ == '__main__':
    unittest.main()
