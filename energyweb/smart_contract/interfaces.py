from energyweb import EnergyData, CarbonEmissionData


class GreenEnergy(EnergyData, CarbonEmissionData):
    """
    Green energy data read from external data sources of energy and carbon emissions
    """

    def __init__(self, energy: EnergyData, carbon_emission: CarbonEmissionData):
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