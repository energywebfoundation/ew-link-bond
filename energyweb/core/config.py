"""
core.config

Configuration file parser and app descriptor
"""
import importlib

from core.integration import EnergyDataSource, CarbonEmissionDataSource, SmartContractClient


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
    def __init__(self, name: str, energy_meter: EnergyDataSource, smart_contract: SmartContractClient):
        if not isinstance(energy_meter, EnergyDataSource):
            raise ConfigurationFileError('Energy_meter must be of an EnergyDataSource class or subclass.')
        if len(name) < 2:
            raise ConfigurationFileError('Name must be longer than two characters.')
        self.name = name
        self.meter = energy_meter
        self.smart_contract = smart_contract


class GreenEnergyProducerConfiguration(EnergyAssetConfiguration):
    """
    Represents special case of energy producer
    """
    def __init__(self, name: str, energy_meter: EnergyDataSource, carbon_emission: CarbonEmissionDataSource,
                 smart_contract: SmartContractClient):
        if not isinstance(carbon_emission, CarbonEmissionDataSource):
            raise ConfigurationFileError('Carbon_emission must be of an CarbonEmissionDataSource class or subclass.')
        self.carbon_emission = carbon_emission
        super().__init__(name=name, energy_meter=energy_meter, smart_contract=smart_contract)


class BulkConfiguration:
    """
    When using one file configuration for multiple assets
    """
    def __init__(self, consumption: [EnergyAssetConfiguration], production: [EnergyAssetConfiguration]):
        self.consumption = consumption
        self.production = production


def parse_bulk(raw_configuration_file: dict) -> BulkConfiguration:
    """
    Read and parse bulk configuration dictionary into structured class instances.
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
    return BulkConfiguration(consumption, production)


def parse_single_asset(raw_configuration_file: dict) -> EnergyAssetConfiguration:
    """
    Read and parse single producer or consumer configuration dictionary into structured class instances.
    :param raw_configuration_file: Configuration file parsed as a dictionary.
    :return: EnergyConsumerConfiguration or EnergyProducerConfiguration
    """
    if not isinstance(raw_configuration_file, dict):
        raise AssertionError("Configuration json must be deserialized first.")
    try:
        configuration = __parse_item(raw_configuration_file)
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
