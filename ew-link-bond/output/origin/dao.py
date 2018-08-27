"""
DAO - Data Access Object
The COO system relies on proofs that are stored on disk and cryptographicaly identified and indexed.
"""

from core import LocalFileData, ChainData
from core.dao import DiskStorage
from core.input import EnergyData, CarbonEmissionData


class ProducedChainData(ChainData):
    """
    Helper for mint_produced
    """
    def __init__(self, energy: int, is_meter_down: bool, previous_hash: str, co2_saved: int, is_co2_down: bool):
        """
        :type previous_hash: previous
        :param energy:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.energy = energy
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash
        self.co2_saved = co2_saved
        self.is_co2_down = is_co2_down


class ConsumedChainData(ChainData):
    """
    Helper for mint_consumed
    """
    def __init__(self, energy: int, previous_hash: str, is_meter_down: bool):
        """
        :type previous_hash: previous
        :param energy:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.energy = energy
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash


class LocalDiskStorage(DiskStorage):

    def add_to_chain(self, data: LocalFileData) -> str:
        """
        Add new file to chain.
        :param data: Data to store
        :return: Base58 hash string
        """
        if isinstance(data, ProductionFileData):
            self.path += 'production/'
        else:
            self.path += 'consumption/'
        super().add_to_chain(data)


class ConsumptionFileData(LocalFileData):
    """
    Structure of every consumption data stored on disk
    """
    def __init__(self, raw_energy: EnergyData, consumed: ConsumedChainData):
        self.raw_energy = raw_energy
        self.consumed = consumed


class ProductionFileData(LocalFileData):
    """
    Structure of every production data stored on disk
    """
    def __init__(self, raw_energy: EnergyData, raw_carbon_emitted: CarbonEmissionData, produced: ProducedChainData):
        self.raw_energy = raw_energy
        self.raw_carbon_emitted = raw_carbon_emitted
        self.produced = produced
