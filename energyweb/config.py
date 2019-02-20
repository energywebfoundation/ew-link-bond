"""
Configuration file parser and app descriptor
"""
import importlib
from collections import namedtuple
from enum import Enum

from ruamel.yaml import YAML

from energyweb import CarbonEmissionAPI
from energyweb.eds.interfaces import EnergyDataSource
from energyweb.smart_contract import EVMSmartContractClient

Module = namedtuple('Module', ['module', 'class_name', 'parameters'])


class MODULES(Enum):
    OriginAPIv1 = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})
    OriginAPIv1Test = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {'url': '', 'source': 'consumed', 'device_id': 0})
    ConsumerTask = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})
    ProducerTask = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})


class ConfigurationFileError(Exception):
    """
    Custom Exception to deal with non-conforming configuration files
    """
    def __init__(self, msg: str = None):
        if not msg:
            super().__init__('Configuration file contain errors. Please provide valid Consumer and/or Producer data.')
        super().__init__(msg)


class EnergyAssetConfiguration:
    """
    Represent Energy Asset configurations for producer and consumers
    """
    def __init__(self, name: str, energy_meter: EnergyDataSource, asset: EVMSmartContractClient):
        if not isinstance(energy_meter, EnergyDataSource):
            raise ConfigurationFileError('Energy_meter must be of an EnergyDataSource class or subclass.')
        if len(name) < 2:
            raise ConfigurationFileError('Name must be longer than two characters.')
        self.name = name
        self.meter = energy_meter
        self.asset = asset


class GreenEnergyProducerConfiguration(EnergyAssetConfiguration):
    """
    Represents special case of energy producer
    """
    def __init__(self, name: str, energy_meter: EnergyDataSource, carbon_emission: CarbonEmissionAPI,
                 asset: EVMSmartContractClient):
        if not isinstance(carbon_emission, CarbonEmissionAPI):
            raise ConfigurationFileError('Carbon_emission must be of an CarbonEmissionAPI class or subclass.')
        self.carbon_emission = carbon_emission
        super().__init__(name=name, energy_meter=energy_meter, asset=asset)


class BondConfiguration:
    """
    Bond configuration file format
    :version v0.3.7
        energyweb: 1.0
        info:
          title: App Title
          description: My very nice energyweb embedded app
          version: 1.0 alpha
        config:
          debugger: on
          verbosity: low
        tasks:
    """
    class AppInfo:
        def __init__(self, title: str, description: str, version: str):
            self.title = title
            self.description = description
            self.version = version

    class AppConfig:
        def __init__(self, debugger: str, verbosity: str, **kwargs):
            self.debugger = debugger
            self.verbosity = verbosity
            self.__dict__.update(kwargs)

    class Submodule:
        def __init__(self, module: str, **kwargs):
            self.module = module
            self.__dict__.update(kwargs)

    def __init__(self, energyweb: str, info: dict, config: dict, tasks: [dict]):
        if len(tasks) < 1:
            raise ConfigurationFileError('Should contain at least one valid task.')
        self.energyweb = energyweb
        self.tasks = tasks
        self.config = self.AppConfig(config)
        self.info = self.AppInfo(info)


def parse_bond_app(configuration_file_path: str) -> BondConfiguration:
    """
    :param configuration_file_path: Configuration file parsed as a dictionary.
    :return: BondConfiguration
    """
    yaml = YAML()  # default, if not specfied, is 'rt' (round-trip)
    try:
        config = yaml.load(open(configuration_file_path))
        # TODO: Continue from here
        version = raw_configuration_file['bond_version']
        tasks = [__parse_instance(task) for task in raw_configuration_file['tasks']]
        configuration = BondConfiguration(bond_version=version, tasks=tasks)
    except Exception:
        raise ConfigurationFileError
    return configuration


def __parse_item(config_item: dict):
    """
    Parse each item of the consumers and producers list.
    :param config_item: Item of the list
    :return: Either Producer or Consumer configuration depending if carbon-emission key is present
    """
    item = {
        'energy_meter': __parse_instance(config_item['energy-meter']),
        'smart_contract': __parse_instance(config_item['smart-contract']),
        'name': config_item['name']
    }
    if 'carbon-emission' not in config_item:
        return EnergyAssetConfiguration(**item)
    else:
        item['carbon_emission'] = __parse_instance(config_item['carbon-emission'])
        return GreenEnergyProducerConfiguration(**item)


def __parse_instance(submodule: dict) -> object:
    """
    Reflection algorithm to dynamically load python modules referenced on the configuration json.
    :param submodule: Configuration dict must have the keys 'module', 'class_name', 'class_parameters'.
    :return: Class instance as in config file.
    """
    module_instance = importlib.import_module(submodule['module'])
    class_obj = getattr(module_instance, submodule['class_name'])
    class_instance = class_obj(**submodule['class_parameters'])
    return class_instance
