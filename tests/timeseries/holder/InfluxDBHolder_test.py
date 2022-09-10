import unittest

from core.options.exception.MissingOptionError import MissingOptionError

from timeseries.holder.InfluxDBHolder import InfluxDBHolder
from timeseries.provider.InfluxDBProvider import InfluxDBProvider


class InfluxDBHolderTestCase(unittest.TestCase):

    def tearDown(self):
        InfluxDBHolder.re_initialize()

    def test_should_initialize_only_one_influxdb_provider_instance(self):
        options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1',
            'INFLUXDB_SERVER_PORT': 8086,
            'INFLUXDB_AUTH_TOKEN': 'q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==',
            'INFLUXDB_AUTH_ORG': 'persuader-technology',
            'INFLUXDB_BUCKET': 'automata',
            'AUTO_CONNECT': False
        }
        db_holder = InfluxDBHolder(options)
        self.assertIsNotNone(db_holder)
        instance_1 = id(InfluxDBHolder(options))
        instance_2 = id(InfluxDBHolder(options))
        self.assertEqual(instance_1, instance_2, 'every instance after should be the same')

    def test_should_not_require_influxdb_provider_options_on_subsequent_calls(self):
        options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1',
            'INFLUXDB_SERVER_PORT': 8086,
            'INFLUXDB_AUTH_TOKEN': 'q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==',
            'INFLUXDB_AUTH_ORG': 'persuader-technology',
            'INFLUXDB_BUCKET': 'automata',
            'AUTO_CONNECT': False
        }
        db_holder = InfluxDBHolder(options)
        self.assertIsNotNone(db_holder)
        instance_1 = id(InfluxDBHolder())
        instance_2 = id(InfluxDBHolder())
        self.assertEqual(instance_1, instance_2, 'every instance after should be the same')

    def test_should_raise_error_when_options_are_missing_and_auto_connect_should_be_false(self):
        with self.assertRaises(MissingOptionError) as mo:
            InfluxDBHolder.re_initialize()
            InfluxDBHolder(None)
        self.assertEqual('missing option please provide options INFLUXDB_SERVER_ADDRESS and INFLUXDB_SERVER_PORT', str(mo.exception))

    def test_should_not_raise_options_errors_when_not_to_auto_connect(self):
        options = {
            'AUTO_CONNECT': False
        }
        InfluxDBHolder.re_initialize()
        db = InfluxDBHolder(options)
        self.assertEqual(False, db.auto_connect)

    def test_should_raise_error_when_influxdb_server_options_are_missing(self):
        options = {}
        with self.assertRaises(MissingOptionError) as mo:
            InfluxDBHolder.re_initialize()
            InfluxDBHolder(options)
        self.assertEqual('missing option please provide option INFLUXDB_SERVER_ADDRESS', str(mo.exception))

    def test_should_raise_error_when_influxdb_server_port_missing(self):
        options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1'
        }
        with self.assertRaises(MissingOptionError) as mo:
            InfluxDBHolder.re_initialize()
            InfluxDBHolder(options)
        self.assertEqual('missing option please provide option INFLUXDB_SERVER_PORT', str(mo.exception))

    def test_should_instantiate_influxdb_provider(self):
        options = {
            'INFLUXDB_SERVER_ADDRESS': '127.0.0.1',
            'INFLUXDB_SERVER_PORT': 8086,
            'INFLUXDB_AUTH_TOKEN': 'q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==',
            'INFLUXDB_AUTH_ORG': 'persuader-technology',
            'INFLUXDB_BUCKET': 'automata',
            'AUTO_CONNECT': False
        }
        db_holder = InfluxDBHolder(options)
        self.assertIsNotNone(db_holder)
        self.assertIsInstance(db_holder, InfluxDBProvider)


if __name__ == '__main__':
    unittest.main()
