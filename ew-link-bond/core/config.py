import json
import importlib

from core import JSONAble
from core.input import EnergyDataSource, CarbonEmissionDataSource
from core.output import SmartContractClient


class Credentials(JSONAble):
    def __init__(self, contract_address: str, wallet_add: str, wallet_pwd: str):
        self.contract_address = contract_address
        self.wallet_add = wallet_add
        self.wallet_pwd = wallet_pwd


class InputConfiguration:

    def __init__(self, energy: EnergyDataSource, credentials: Credentials, carbon_emission: CarbonEmissionDataSource, name: str):
        if not isinstance(energy, EnergyDataSource):
            raise AttributeError
        if not isinstance(credentials, Credentials):
            raise AttributeError
        if carbon_emission is not None and not isinstance(carbon_emission, CarbonEmissionDataSource):
            raise AttributeError
        self.energy = energy
        self.origin = credentials
        self.carbon_emission = carbon_emission
        self.name = name


class Configuration:

    def __init__(self, production: [InputConfiguration], consumption: [InputConfiguration], client: SmartContractClient):
        self.production = production
        self.consumption = consumption
        self.client = client

    def __check(self, production, consumption, client):
        [self.__check_input_config(item) for item in production]
        [self.__check_input_config(item) for item in consumption]
        if not issubclass(client.__class__, SmartContractClient):
            raise AttributeError('Must have strictly one blockchain client.')

    @staticmethod
    def __check_input_config(obj):
        if not isinstance(obj, InputConfiguration):
            raise AttributeError('Configuration file contain errors.')


def __get_input_configuration(configuration: dict) -> InputConfiguration:
    # TODO: Conform to new config file
    emission = 'carbonemission' in configuration
    instance = {
        "energy": __get_class_instance(configuration['energy']),
        "carbon_emission": __get_class_instance(configuration['carbonemission']) if emission else None,
        "origin": __get_class_instance(configuration['origin']),
        "name": configuration['name']
    }
    if not instance['name']:
        raise ImportError('Configuration lacks `name` field.')
    return InputConfiguration(**instance)


def __get_configuration(input_configuration_list: list) -> [InputConfiguration]:
    if not input_configuration_list:
        return None
    return [__get_input_configuration(configuration) for configuration in input_configuration_list]


def __get_class_instance(submodule: dict) -> object:
    """
    Reflection algorithm to dynamically load python modules referenced on the configuration json.
    :param submodule: Configuration dict must have the keys 'module', 'class_name', 'class_parameters'.
    :return: Class instance as in config file.
    """
    module_instance = importlib.import_module(submodule['module'])
    class_obj = getattr(module_instance, submodule['class_name'])
    class_instance = class_obj(**submodule['class_parameters'])
    return class_instance


def parse_file(config_file_path: str) -> Configuration:
    """
    Read config file into structured class instances.
    :param config_file_path: File system path to json format file.
    :return: Configuration instance
    """
    config_json = json.load(open(config_file_path))
    return parse(config_json)


def parse(config_dict: dict) -> Configuration:
    """
    Read config file into structured class instances.
    :param config_dict: Config dictionary.
    :return: Configuration instance
    """
    if not isinstance(config_dict, dict):
        print("Config type should be dict. Type found is:")
        print(type(config_dict))
        raise AssertionError
    is_consuming = 'consumption' in config_dict
    is_producing = 'production' in config_dict
    instance = {
        "consumption": __get_configuration(config_dict['consumption'] if is_consuming else None),
        "production": __get_configuration(config_dict['production'] if is_producing else None),
        "client": __get_class_instance(config_dict['client'])
    }
    return Configuration(**instance)
