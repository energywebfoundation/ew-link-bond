import inspect
import datetime
from enum import IntEnum


class Serializable(object):
    """
    Object serialization helper
    """
    def __iter__(self):
        for attr, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                iso = value.isoformat()
                yield attr, iso
            elif hasattr(value, '__iter__'):
                if hasattr(value, 'pop'):
                    a = []
                    for item in value:
                        if hasattr(item, '__iter__'):
                            a.append(dict(item))
                        else:
                            a.append(item)
                    yield attr, a
                else:
                    yield attr, dict(value)
            else:
                yield attr, value

    def to_dict(self):
        result = {}
        init = getattr(self, '__init__')
        for parameter in inspect.signature(init).parameters:
            att = getattr(self, parameter)
            if isinstance(att, list) or isinstance(att, set):
                att = [self.to_dict_or_self(o) for o in att]
            if isinstance(att, (datetime.datetime, datetime.date)):
                att = att.isoformat()
            result[parameter] = self.to_dict_or_self(att)
        return result

    @staticmethod
    def to_dict_or_self(obj):
        to_dict = getattr(obj, 'to_dict', None)
        if to_dict:
            return to_dict()
        else:
            return obj


class ExternalData(Serializable):
    """
    Encapsulates collected data in a traceable fashion
    """

    def __init__(self, access_epoch, raw):
        """
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected in the device
        """
        self.access_epoch = access_epoch
        self.raw = raw


class EnergyUnit(IntEnum):
    """
    Possible units for effort and billing purposes. Determines the convertion algorithms.
    """
    JOULES = 0
    WATT_HOUR = 1
    KILOWATT_HOUR = 2
    MEGAWATT_HOUR = 3
    GIGAWATT_HOUR = 4


class RawEnergyData(ExternalData):
    """
    Standard for collected energy and power data, to be transformed into mintable data.
    """

    def __init__(self, asset, access_epoch, raw, energy, measurement_epoch):
        """
        Minimum set of data for power measurement logging.
        :param asset: Metadata about the measurement device
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        :param energy: Measured energy at the source converted to watt-hours
        :param measurement_epoch: Time of measurement at the source
        """
        self.asset = asset
        self.measurement_epoch = measurement_epoch
        self.energy = energy
        ExternalData.__init__(self, access_epoch, raw)


class RawCarbonEmissionData(ExternalData):
    """
    Standard for collected carbon emission data, to be transformed into mintable data.
    """

    def __init__(self, access_epoch, raw, accumulated_co2, measurement_epoch):
        """
        Minimum set of data for power measurement logging.
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        :param accumulated_co2: Registered in kg of carbon dioxide
        :param measurement_epoch: Time of measurement at the source
        """
        self.accumulated_co2 = accumulated_co2
        self.measurement_epoch = measurement_epoch
        ExternalData.__init__(self, access_epoch, raw)


class Energy(Serializable):
    """
    Represents energy measured and converted, ready to be logged and minted in the blockchain
    """


class GreenEnergy(ExternalData):
    """
    Green energy data read from external data sources of energy and carbon emissions
    """
    def __init__(self, energy: RawEnergyData, carbon_emission: RawCarbonEmissionData):
        self.energy = energy
        self.carbon_emission = carbon_emission
        super().__init__(None, None)

    def co2_saved(self, energy_offset: int = 0):
        """
        Returns amount of carbon dioxide saved
        :param energy_offset: Energy already registered to add up in case the energy measured was not accumulated
        :return: Total amount of kg of carbon dioxide
        """
        if not self.carbon_emission:
            return 0
        accumulated_energy = self.energy.energy
        if not self.energy.asset.is_accumulated:
            accumulated_energy += energy_offset
        co2_saved = self.carbon_emission.accumulated_co2
        calculated_co2 = accumulated_energy * co2_saved
        co2_saved = int(calculated_co2 * pow(10, 3))
        return co2_saved


class EnergyAsset(Serializable):
    """
    Energy asset device abstraction. Can be smart-meters, battery controllers, inverters, gateways.
    """
    def __init__(self, manufacturer, model, serial_number, latitude, longitude, energy_unit, is_value_accumulated):
        """
        :param manufacturer: EnergyAsset Manufacturer
        :param model: EnergyAsset model
        :param serial_number: EnergyAsset Serial Number
        :param latitude: EnergyAsset geolocation latitude
        :param longitude: EnergyAsset geolocation longitude
        :param energy_unit: Energy unity
        :param is_value_accumulated: Flags if the api provides accumulated power or hourly production
        """
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.latitude = latitude
        self.longitude = longitude
        self.energy_unit = EnergyUnit[energy_unit.upper()]
        self.is_value_accumulated = is_value_accumulated


class BlockchainClient:
    """
    Abstract blockchain client abstraction
    """

    def is_synced(self) -> bool:
        """
        Compares latest block from peers with client's last synced block.
        :return: Synced status
        :rtype: bool
        """
        raise NotImplementedError

    def call(self, address: str, contract_name: str, method_name: str, password: str, args=None) -> dict:
        """
        Calls a method in a smart-contract
        Sends a transaction to the Blockchain and awaits for mining until a receipt is returned.
        :param address: Contract address
        :param contract_name: Name of the contract in contracts
        :param method_name: Use the same name as found in the contract abi
        :param password: String of the raw password
        :param args: Method parameters
        :return: Transaction receipt
        :rtype: dict
        """
        raise NotImplementedError

    def send(self, address: str, contract_name: str, method_name: str, password: str, args=None) -> dict:
        """
        Send a transaction to execute a method in a smart-contract
        Sends a transaction to the Blockchain and awaits for mining until a receipt is returned.
        :param address: Contract address
        :param contract_name: Name of the contract in contracts
        :param method_name: Use the same name as found in the contract abi
        :param password: String of the raw password
        :param args: Method parameters
        :return: Transaction receipt
        :rtype: dict
        """
        raise NotImplementedError

    def mint(self, energy: Energy) -> dict:
        """
        Mint the measured energy in the blockchain smart-contract
        """
        raise NotImplementedError
