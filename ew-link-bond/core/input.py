"""
General & energy related data input interfaces
"""
from enum import IntEnum

from core import JSONAble
from core.event_loop import LifeCycle


class Device(JSONAble):
    """
    Data gathering device abstraction
    """

    def __init__(self, manufacturer, model, serial_number, latitude, longitude, energy_unit, is_accumulated):
        """
        :param manufacturer: Device Manufacturer
        :param model: Device model
        :param serial_number: Device Serial Number
        :param latitude: Device geolocation latitude
        :param longitude: Device geolocation longitude
        :param energy_unit: Energy unity
        :param is_accumulated: Flags if the api provides accumulated power or hourly production
        """
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.latitude = latitude
        self.longitude = longitude
        self.energy_unit = EnergyUnit[energy_unit.upper()]
        self.is_accumulated = is_accumulated


class ExternalData(JSONAble):
    """
    Encapsulates collected data in a traceable fashion
    """

    def __init__(self, access_epoch, raw):
        """
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        """
        self.access_epoch = access_epoch
        self.raw = raw


class ExternalDataSource(JSONAble):
    """
    Interface to enforce correct return type and standardized naming
    """
    def __init__(self, read_cycle: LifeCycle = LifeCycle.TWELVE_HOURS):
        self.read_cycle = read_cycle

    def read_state(self, *args, **kwargs) -> ExternalData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: ExternalData
        """
        raise NotImplementedError


class EnergyUnit(IntEnum):
    """
    Possible units for effort and billing purposes. Determines the convertion algorithms.
    """
    JOULES = 0
    WATT_HOUR = 1
    KILOWATT_HOUR = 2
    MEGAWATT_HOUR = 3
    GIGAWATT_HOUR = 4


class EnergyData(ExternalData):
    """
    Standard for energy and power data used as input
    """

    def __init__(self, device, access_epoch, raw, energy, measurement_epoch):
        """
        Minimum set of data for power measurement logging.
        :param device: Metadata about the measurement device
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        :param energy: Measured energy at the source converted to watt-hours
        :param measurement_epoch: Time of measurement at the source
        """
        self.device = device
        self.measurement_epoch = measurement_epoch
        self.energy = energy
        ExternalData.__init__(self, access_epoch, raw)


class EnergyDataSource(ExternalDataSource):

    def read_state(self, *args, **kwargs) -> EnergyData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: EnergyData
        """

    @staticmethod
    def to_mwh(energy: int, unit):
        """
        Converts energy measured value in predefined unit to Megawatt-Hour
        :param unit: EnergyUnit
        :param energy: Value measured at the source
        :return: Value converted to MWh
        :rtype: float
        """
        convert = lambda x: float(energy) / x
        return {
            EnergyUnit.WATT_HOUR: convert(10 ** 6),
            EnergyUnit.KILOWATT_HOUR: convert(10 ** 3),
            EnergyUnit.MEGAWATT_HOUR: convert(1),
            EnergyUnit.GIGAWATT_HOUR: convert(1 * 10 ** -3),
            EnergyUnit.JOULES: convert(1 * 2.77778 * 10 ** -10),
        }.get(unit)

    @staticmethod
    def to_wh(energy: int, unit: EnergyUnit):
        """
        Converts energy measured value in predefined unit to Watt-Hour
        :param unit: EnergyUnit
        :param energy: Value measured at the source
        :return: Value converted to MWh
        :rtype: int
        """
        convert = lambda x: int(float(energy * x))
        return {
            EnergyUnit.WATT_HOUR: convert(1),
            EnergyUnit.KILOWATT_HOUR: convert(10 ** 3),
            EnergyUnit.MEGAWATT_HOUR: convert(10 ** 6),
            EnergyUnit.GIGAWATT_HOUR: convert(10 ** 9),
            EnergyUnit.JOULES: convert(1 * 2.77778 * 10 ** -1),
        }.get(unit)


class CarbonEmissionData(ExternalData):
    """
    Standard for carbon emission data used as input
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


class CarbonEmissionDataSource(ExternalDataSource):

    def read_state(self, *args, **kwargs) -> CarbonEmissionData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: CarbonEmissionData
        """


class CleanEnergy(JSONAble):
    """
    Clean energy data read from external data sources of energy and carbon emissions
    """

    def __init__(self, energy: EnergyData, carbon_emission: CarbonEmissionData):
        self.energy = energy
        self.carbon_emission = carbon_emission

    def co2_saved(self, energy_offset: int = 0):
        """
        Returns amount of carbon dioxide saved
        :param energy_offset: Energy already registered to add up in case the energy measured was not accumulated
        :return: Total amount of kg of carbon dioxide
        """
        if not self.carbon_emission:
            return 0
        accumulated_energy = self.energy.energy
        if not self.energy.device.is_accumulated:
            accumulated_energy += energy_offset
        co2_saved = self.carbon_emission.accumulated_co2
        calculated_co2 = accumulated_energy * co2_saved
        co2_saved = int(calculated_co2 * pow(10, 3))
        return co2_saved
