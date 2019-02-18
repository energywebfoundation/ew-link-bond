"""
Energy Data Sources Library
Bundles integration points for collecting data from Energy Assets such as but not limited to: energy meters, batteries, and frequency inverters.
"""
from energyweb import ExternalDataSource, RawEnergyData, EnergyUnit


class EnergyDataSource(ExternalDataSource):
    """
    Energy endpoint data interface
    """

    def read_state(self, *args, **kwargs) -> RawEnergyData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: RawEnergyData
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