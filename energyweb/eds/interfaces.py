from enum import IntEnum

from energyweb.interfaces import ExternalData, IntegrationPoint


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
    Standard for collected energy and power data, to be transformed into mintable data.
    """

    def __init__(self, device, access_epoch, raw, energy, measurement_epoch):
        """
        Minimum set of data for power measurement logging.
        :param device: Metadata about the measurement device. EnergyDevice
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        :param energy: Measured energy at the source converted to watt-hours
        :param measurement_epoch: Time of measurement at the source
        """
        self.device = device
        self.measurement_epoch = measurement_epoch
        self.energy = energy
        ExternalData.__init__(self, access_epoch, raw)


class EnergyDevice(IntegrationPoint):
    """
    Energy device or api abstraction. Can be smart-meters, battery controllers, inverters, gateways, clouds, so on.
    """

    def __init__(self, manufacturer, model, serial_number, energy_unit, is_accumulated, latitude=None, longitude=None):
        """
        :param manufacturer: EnergyAsset Manufacturer
        :param model: EnergyAsset model
        :param serial_number: EnergyAsset Serial Number
        :param latitude: EnergyAsset geolocation latitude
        :param longitude: EnergyAsset geolocation longitude
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

    def read_state(self, *args, **kwargs) -> EnergyData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: EnergyData
        """
        raise NotImplementedError

    def write_state(self, *args, **kwargs) -> EnergyData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: EnergyData
        """
        raise NotImplementedError

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
