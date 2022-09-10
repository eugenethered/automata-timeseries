import logging
from typing import TypeVar, Type

from timeseries.provider.InfluxDBProvider import InfluxDBProvider

T = TypeVar('T')


class InfluxDBHolder:
    __instance: T = None

    def __new__(cls, options=None, held_type: Type[T] = InfluxDBProvider) -> T:
        if cls.__instance is None:
            log = logging.getLogger('InfluxDBHolder')
            log.info(f'Holder obtaining InfluxDB provider with options:{options}')
            auto_connect = cls.set_auto_connect(options)
            cls.__instance = held_type(options, auto_connect)
        return cls.__instance

    @staticmethod
    def set_auto_connect(options):
        if options is None:
            return False
        if 'AUTO_CONNECT' not in options:
            return True
        return options['AUTO_CONNECT']

    @staticmethod
    def re_initialize():
        InfluxDBHolder.__instance = None

