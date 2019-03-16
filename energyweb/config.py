"""
Configuration file parser and app descriptor
"""
import importlib
from collections import namedtuple
from enum import Enum

from energyweb.carbonemission import CarbonEmissionAPI
from energyweb.eds.interfaces import EnergyDevice
from energyweb.smart_contract.interfaces import EVMSmartContractClient

Module = namedtuple('Module', ['module', 'class_name', 'parameters'])


class MODULES(Enum):
    OriginAPIv1 = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})
    OriginAPIv1Test = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {'url': '', 'source': 'consumed', 'device_id': 0})
    ConsumerTask = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})
    ProducerTask = Module('energyweb.smart_meter.energy_api', 'OriginAPIv1', {})


class EnergyAssetConfiguration:
    """
    Represent Energy Asset configurations for producer and consumers
    """
    def __init__(self, name: str, energy_meter: EnergyDevice, asset: EVMSmartContractClient):
        if not isinstance(energy_meter, EnergyDevice):
            raise ConfigurationFileError('Energy_meter must be of an EnergyDevice class or subclass.')
        if len(name) < 2:
            raise ConfigurationFileError('Name must be longer than two characters.')
        self.name = name
        self.meter = energy_meter
        self.asset = asset


class GreenEnergyProducerConfiguration(EnergyAssetConfiguration):
    """
    Represents special case of energy producer
    """
    def __init__(self, name: str, energy_meter: EnergyDevice, carbon_emission: CarbonEmissionAPI,
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
          command: My very nice energyweb embedded app
          version: 1.0 alpha
        task_config:
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

# TODO: Refactor origin config and decide if it lives here or in origin app
# def parse_bond_app(configuration_file_path: str) -> BondConfiguration:
#     """
#     :param configuration_file_path: Configuration file parsed as a dictionary.
#     :return: BondConfiguration
#     """
#     from ruamel.yaml import YAML
#     yaml = YAML()  # default, if not specfied, is 'rt' (round-trip)
#     try:
#         config = yaml.load(open(configuration_file_path))
#
#         version = config['bond_version']
#         tasks = [__parse_instance(task) for task in config['tasks']]
#         configuration = BondConfiguration(bond_version=version, tasks=tasks)
#     except Exception:
#         raise ConfigurationFileError
#     return configuration


class ConfigurationFileError(Exception):
    """
    Custom Exception to deal with non-conforming configuration files
    """
    def __init__(self, msg: str = None):
        if not msg:
            super().__init__('Configuration file contain errors. Please provide valid Consumer and/or Producer data.')
        super().__init__(msg)


class EnergywebAppConfiguration:
    """
    Abstract class
    """
    pass


class CooV1ConsumerConfiguration(EnergywebAppConfiguration):
    """
    Represent Energy Asset configurations for producer and consumers
    """
    def __init__(self, name: str, energy_meter: EnergyDevice, smart_contract: EVMSmartContractClient):
        if not isinstance(energy_meter, EnergyDevice):
            raise ConfigurationFileError('Energy_meter must be of an EnergyDevice class or subclass.')
        if len(name) < 2:
            raise ConfigurationFileError('Name must be longer than two characters.')
        self.name = name
        self.energy_meter = energy_meter
        self.smart_contract = smart_contract


class CooV1ProducerConfiguration(CooV1ConsumerConfiguration):
    """
    Represents special case of energy producer
    """
    def __init__(self, name: str, energy_meter: EnergyDevice, carbon_emission: CarbonEmissionAPI,
                 smart_contract: EVMSmartContractClient):
        if not isinstance(carbon_emission, CarbonEmissionAPI):
            raise ConfigurationFileError('Carbon_emission must be of an CarbonEmissionAPI class or subclass.')
        self.carbon_emission = carbon_emission
        super().__init__(name=name, energy_meter=energy_meter, smart_contract=smart_contract)


class CooV1Configuration(EnergywebAppConfiguration):
    """
    When using one file configuration for multiple assets
    """
    def __init__(self, consumption: [CooV1ConsumerConfiguration], production: [CooV1ConsumerConfiguration]):
        self.consumption = consumption
        self.production = production


def parse_coo_v1(raw_configuration_file: dict) -> CooV1Configuration:
    """
    Read and parse Certificatate of Orign v1 (release A) configuration dictionary into structured class instances.
    :param raw_configuration_file: Configuration file parsed as a dictionary.
    :return: Configuration instance
    """
    if not isinstance(raw_configuration_file, dict):
        raise AssertionError("Configuration json must be deserialized first.")
    is_consuming = 'consumers' in raw_configuration_file
    is_producing = 'producers' in raw_configuration_file
    if not is_consuming and not is_producing:
        raise ConfigurationFileError

    consumption = [__parse_item(config) for config in raw_configuration_file['consumers']]
    production = [__parse_item(config) for config in raw_configuration_file['producers']]
    return CooV1Configuration(consumption, production)


def parse_single_asset(raw_configuration_file: dict) -> CooV1ConsumerConfiguration:
    """
    Read and parse single producer or consumer configuration dictionary into structured class instances.
    :param raw_configuration_file: Configuration file parsed as a dictionary.
    :return: EnergyConsumerConfiguration or EnergyProducerConfiguration
    """
    if not isinstance(raw_configuration_file, dict):
        raise AssertionError("Configuration json must be deserialized first.")
    configuration = __parse_item(raw_configuration_file)


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
        return CooV1ConsumerConfiguration(**item)
    else:
        item['carbon_emission'] = __parse_instance(config_item['carbon-emission'])
        return CooV1ProducerConfiguration(**item)


def __parse_instance(submodule: dict) -> object:
    """
    Reflection algorithm to dynamically load python modules referenced on the configuration json.
    :param submodule: Configuration dict must have the keys 'module', 'class_name', 'class_parameters'.
    :return: Class instance as in task_config file.
    """
    module_instance = importlib.import_module(submodule['module'])
    class_obj = getattr(module_instance, submodule['class_name'])
    class_instance = class_obj(**submodule['class_parameters'])
    return class_instance