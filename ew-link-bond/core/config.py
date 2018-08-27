import importlib

from core.input import EnergyDataSource, CarbonEmissionDataSource
from core.output import SmartContractClient


class ConsumerConfiguration:
    """
    Represents one user-provided energy consuming asset
    """

    def __init__(self, name: str, energy_meter: EnergyDataSource, smart_contract: SmartContractClient):
        if not isinstance(energy_meter, EnergyDataSource):
            raise AttributeError
        if len(name) < 2:
            raise AttributeError
        self.name = name
        self.energy = energy_meter
        self.smart_contract = smart_contract


class ProducerConfiguration(ConsumerConfiguration):
    """
    Represents one user-provided energy producing asset
    """

    def __init__(self, name: str, energy_meter: EnergyDataSource, carbon_emission: CarbonEmissionDataSource, smart_contract: SmartContractClient):
        if carbon_emission is not None and not isinstance(carbon_emission, CarbonEmissionDataSource):
            raise AttributeError
        self.carbon_emission = carbon_emission
        super().__init__(name=name, energy_meter=energy_meter, smart_contract=smart_contract)


class Configuration:
    """
    Represents the user-provided parsed configuration json
    """

    def __init__(self, consumption: [ConsumerConfiguration], production: [ProducerConfiguration]):
        [self.__check(item, ConsumerConfiguration) for item in consumption]
        [self.__check(item, ProducerConfiguration) for item in production]
        self.consumption = consumption
        self.production = production

    @staticmethod
    def __check(item, cls):
        if not isinstance(item, cls):
            raise ConfigurationFileError


class ConfigurationFileError(Exception):
    """
    Custom Exception to deal with non-conforming configuration files
    """

    def __init__(self):
        super().__init__('Configuration file contain errors. Please provide valid Consumer and/or Producer data.')


def parse(raw_configuration_file: dict) -> Configuration:
    """
    Read and parse config file into structured class instances.
    :param raw_configuration_file: Configuration file parsed as a dictionary.
    :return: Configuration instance
    """
    if not isinstance(raw_configuration_file, dict):
        print("Config type should be dict. Type found is:")
        print(type(raw_configuration_file))
        raise AssertionError
    is_consuming = 'consumption' in raw_configuration_file
    is_producing = 'production' in raw_configuration_file
    if not is_consuming and not is_producing:
        raise ConfigurationFileError

    consumption = [__parse_item(config) for config in raw_configuration_file['consumption']]
    production = [__parse_item(config) for config in raw_configuration_file['production']]
    return Configuration(consumption, production)


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
        return ConsumerConfiguration(**item)
    else:
        item['carbon_emission'] = __parse_instance(config_item['carbon-emission'])
        return ProducerConfiguration(**item)


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
