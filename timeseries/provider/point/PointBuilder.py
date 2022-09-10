from core.number.BigFloat import BigFloat
from coreutility.date.NanoTimestamp import NanoTimestamp
from influxdb_client import Point


def build_point(measurement, instrument, price: BigFloat, nano_timestamp=None) -> Point:
    point = Point(measurement).tag("instrument", instrument).field("price", str(price))
    if nano_timestamp is None:
        point.time(NanoTimestamp.get_nanoseconds())
    else:
        nano_time_to_use = nano_timestamp if is_full_nanotime(nano_timestamp) else NanoTimestamp.get_nanoseconds()
        point.time(nano_time_to_use)
    return point


def is_full_nanotime(value):
    return True if len(str(value)) == 19 else False
