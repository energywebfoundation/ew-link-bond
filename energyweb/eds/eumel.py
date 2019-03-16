"""
input.eumel

Library containing the implementations of Eumel DataLogger integration classes
"""
import time
import requests

from xml.etree import ElementTree
from energyweb.eds import EnergyUnit, EnergyData
from energyweb.eds.interfaces import EnergyDevice


class DataLoggerV1(EnergyDevice):
    """
    Eumel DataLogger api v1.0 access implementation
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user: User configured on the devices
        :param password: Password for this user
        """
        self.eumel_api_url = ip + '/rest'
        self.auth = (user, password)
        super().__init__(manufacturer='Verbund', model='Eumel v1', serial_number=None, energy_unit=EnergyUnit.WATT_HOUR,
                         is_accumulated=True)

    def read_state(self, path=None) -> EnergyData:
        if path:
            tree = ElementTree.parse(path)
            with open(path) as file:
                raw = file.read()
        else:
            http_packet = requests.get(self.eumel_api_url, auth=self.auth)
            raw = http_packet.content.decode()
            tree = ElementTree.parse(raw)
        tree_root = tree.getroot()
        tree_header = tree_root[0].attrib
        tree_leaves = {child.attrib['id']: child.text for child in tree_root[0][0]}
        device = EnergyDevice(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'],
            energy_unit=self.energy_unit,
            is_accumulated=self.is_accumulated)
        access_epoch = int(time.time())
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        energy = float(tree_leaves['TotWhImp'].replace('.', ''))
        mwh_energy = self.to_mwh(energy, self.energy_unit)
        measurement_epoch = int(time.mktime(time.strptime(tree_header['t'], time_format)))
        return EnergyData(asset=device, access_epoch=access_epoch, raw=raw, measurement_epoch=measurement_epoch,
                          energy=mwh_energy)

    def write_state(self, *args, **kwargs):
        raise NotImplementedError


class DataLoggerV2d1d1(EnergyDevice):
    """
    Eumel DataLogger api v2.1.1 access implementation
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user: User configured on the devices
        :param password: Password for this user
        """
        self.eumel_api_url = ip + '/wizard/public/api/rest'
        self.auth = (user, password)
        super().__init__(manufacturer='Verbund', model='Eumel v1', serial_number=None, energy_unit=EnergyUnit.WATT_HOUR,
                         is_accumulated=True)

    def read_state(self, path=None) -> EnergyData:
        if path:
            tree = ElementTree.parse(path)
            with open(path) as file:
                raw = file.read()
        else:
            http_packet = requests.get(self.eumel_api_url, auth=self.auth)
            raw = http_packet.content.decode()
            tree = ElementTree.ElementTree(ElementTree.fromstring(raw))
        tree_root = tree.getroot()
        tree_header = tree_root[0].attrib
        tree_leaves = {child.attrib['id']: child.text for child in tree_root[0][1]}
        device = EnergyDevice(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'],
            energy_unit=self.energy_unit,
            is_accumulated=self.is_accumulated)
        access_epoch = int(time.time())
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        energy = float(tree_leaves['TotWhImp'])
        mwh_energy = self.to_mwh(energy, self.energy_unit)
        measurement_epoch = int(time.mktime(time.strptime(tree_header['t'], time_format)))
        return EnergyData(asset=device, access_epoch=access_epoch, raw=raw, measurement_epoch=measurement_epoch,
                          energy=mwh_energy)

    def write_state(self, *args, **kwargs):
        raise NotImplementedError
