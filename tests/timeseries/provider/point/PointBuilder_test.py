import unittest

from core.number.BigFloat import BigFloat

from timeseries.provider.point.PointBuilder import build_point


class PointBuilderTestCase(unittest.TestCase):

    def test_should_build_point_with_supplied_nano_timestamp(self):
        point = build_point('timeseries-test', 'test', BigFloat('100.0'), 1662473484448608385)
        expected_line = 'timeseries-test,instrument=test price="100.0" 1662473484448608385'
        self.assertEqual(point.to_line_protocol(), expected_line)

    def test_should_build_point_with_generated_timestamp(self):
        point = build_point('timeseries-test', 'test', BigFloat('100.0'))
        self.assertRegex(point.to_line_protocol(), r'^timeseries-test,instrument=test price="100.0" \d{19}$')

    def test_should_build_point_but_override_supplied_timestamp_when_not_full_nanotime(self):
        point = build_point('timeseries-test', 'test', BigFloat('123.45'), 1648913430060)
        self.assertRegex(point.to_line_protocol(), r'^timeseries-test,instrument=test price="123.45" \d{19}$')


if __name__ == '__main__':
    unittest.main()
