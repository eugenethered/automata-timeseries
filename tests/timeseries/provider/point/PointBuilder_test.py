import unittest

from timeseries.provider.point.PointBuilder import build_point


class PointBuilderTestCase(unittest.TestCase):

    def test_should_build_point_with_supplied_nano_timestamp(self):
        point = build_point('timeseries-test', 'test', 100.0, 1662473484448608385)
        expected_line = 'timeseries-test,instrument=test price=100 1662473484448608385'
        self.assertEqual(point.to_line_protocol(), expected_line)

    def test_should_build_point_with_generated_timestamp(self):
        point = build_point('timeseries-test', 'test', 100.0)
        self.assertRegex(point.to_line_protocol(), r'^timeseries-test,instrument=test price=100 \d{19}$')


if __name__ == '__main__':
    unittest.main()
