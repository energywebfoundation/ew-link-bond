"""
Library containing the implementations of smart-meter simulator integration classes
"""
import time
import random

from energyweb.integration import EnergyDataSource
from energyweb import RawEnergyData, EnergyAsset


class EnergyMeterSimulator(EnergyDataSource):
    """
    Data logger simulator. It will return a pseudo-random incremental number in every iteration
    """
    def __init__(self):
        self.memory = random.randint(1, 20)

    def read_state(self) -> RawEnergyData:
        access_epoch = int(time.time())
        device = EnergyAsset(
            manufacturer='Slock.it',
            model='Virtual Energy Meter',
            serial_number='0001000',
            latitude='1.123',
            longitude='1.321')
        kwh_power = random.randint(self.memory, (self.memory + 1) + 20)
        measurement_epoch = int(time.time())
        device_str = device.manufacturer + device.model + device.serial_number
        raw = str(device_str + str(access_epoch) + str(kwh_power) + str(measurement_epoch))
        return RawEnergyData(asset=device, access_epoch=access_epoch, raw=raw, energy=kwh_power,
                             measurement_epoch=measurement_epoch)
