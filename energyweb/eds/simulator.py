"""
Library containing the implementations of smart-energy_meter simulator integration classes
"""
import time
import random

from energyweb.eds.interfaces import EnergyDevice, EnergyData

class EnergyMeterSimulator(EnergyDevice):
    """
    Data logger simulator. It will return a pseudo-random incremental number in every iteration
    """
    def __init__(self):
        self.memory = random.randint(1, 20)

    def read_state(self) -> EnergyData:
        access_epoch = int(time.time())
        device = EnergyDevice(
            manufacturer='Slock.it',
            model='Virtual Energy Meter',
            serial_number='0001000',
            latitude='1.123',
            longitude='1.321')
        kwh_power = random.randint(self.memory, (self.memory + 1) + 20)
        measurement_epoch = int(time.time())
        device_str = device.manufacturer + device.model + device.serial_number
        raw = str(device_str + str(access_epoch) + str(kwh_power) + str(measurement_epoch))
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, energy=kwh_power,
                          measurement_epoch=measurement_epoch)

    def write_state(self, *args, **kwargs):
        raise NotImplementedError
