"""
input.eumel

Library containing the implementations of Eumel DataLogger integration classes
"""
import time
import requests

from xml.etree import ElementTree
from core.integration import EnergyDataSource
from core import EnergyUnit, RawEnergyData, EnergyAsset


class DataLoggerV1(EnergyDataSource):
    """
    Eumel DataLogger api v1.0 access implementation

    unit: Watthour
    is_accumulated: True
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user: User configured on the devices
        :param password: Password for this user
        """
        self.eumel_api_url = ip + '/rest'
        self.auth = (user, password)
        super().__init__(unit=EnergyUnit.WATT_HOUR, is_accumulated=True)

    def read_state(self, path=None) -> RawEnergyData:
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
        device = EnergyAsset(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'])
        access_epoch = int(time.time())
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        energy = float(tree_leaves['TotWhImp'].replace('.', ''))
        mwh_energy = self.energy_in_mwh(energy)
        measurement_epoch = int(time.mktime(time.strptime(tree_header['t'], time_format)))
        return RawEnergyData(asset=device, access_epoch=access_epoch, raw=raw, mwh_energy=mwh_energy, unit=self.unit,
                             measurement_epoch=measurement_epoch, is_accumulated=self.is_accumulated)


class DataLoggerV2d1d1(EnergyDataSource):
    """
    Eumel DataLogger api v2.1.1 access implementation

    unit: Watthour
    is_accumulated: True
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user: User configured on the devices
        :param password: Password for this user
        """
        self.eumel_api_url = ip + '/wizard/public/api/rest'
        self.auth = (user, password)
        super().__init__(unit=EnergyUnit.WATT_HOUR, is_accumulated=True)

    def read_state(self, path=None) -> RawEnergyData:
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
        device = EnergyAsset(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'],
            geolocation=None)
        access_epoch = int(time.time())
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        energy = float(tree_leaves['TotWhImp'])
        mwh_energy = self.energy_in_mwh(energy)
        measurement_epoch = int(time.mktime(time.strptime(tree_header['t'], time_format)))
        return RawEnergyData(asset=device, access_epoch=access_epoch, raw=raw, mwh_energy=mwh_energy, unit=self.unit,
                             measurement_epoch=measurement_epoch, is_accumulated=self.is_accumulated)
