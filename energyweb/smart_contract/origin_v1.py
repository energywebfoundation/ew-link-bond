"""
Library containing the Certificate of Origin v1.0 integration classes
"""
from energyweb.eds.interfaces import EnergyData
from energyweb.smart_contract.interfaces import EVMSmartContractClient
from energyweb.smart_contract.origin.consumer_v1 import contract as consumer_v1
from energyweb.smart_contract.origin.producer_v1 import contract as producer_v1
from energyweb.smart_contract.origin.asset_reg_v1 import contract as asset_reg_v1


class ProducedEnergy(EnergyData):
    """
    Helper for coo smart-contract mint_produced method
    """
    def __init__(self, value: int, is_meter_down: bool, previous_hash: str, co2_saved: int, is_co2_down: bool):
        """
        :type previous_hash: previous
        :param value:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.value = value
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash
        self.co2_saved = co2_saved
        self.is_co2_down = is_co2_down


class ConsumedEnergy(EnergyData):
    """
    Helper for coo smart-contract mint_consumed method
    """
    def __init__(self, value: int, previous_hash: str, is_meter_down: bool):
        """
        :type previous_hash: previous
        :param value:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.value = value
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash


class OriginV1(EVMSmartContractClient):
    """
    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def mint(self, energy: EnergyData) -> dict:
        raise NotImplementedError

    def __init__(self, asset_id: int, wallet_add: str, wallet_pwd: str, client_url: str):
        """
        :param asset_id: ID received in device registration.
        :param wallet_add: Network wallet address
        :param wallet_add: Network wallet password
        :param client_url: URL like address to the blockchain client api.
        contract_address is not used from task_config
        """
        contracts = {
            "producer": producer_v1,
            "consumer": consumer_v1,
            "asset_reg": asset_reg_v1
        }
        credentials = (wallet_add, wallet_pwd)
        max_retries = 1000
        retry_pause = 5

        self.asset_id = asset_id
        super().__init__(credentials, contracts, client_url, max_retries, retry_pause)

    def register_asset(self, country: str, region: str, zip_code: str, city: str, street: str, house_number: str,
                       latitude: str, longitude: str):
        """
        Register device. The account signing the transaction must have "AssetAdmin" role to successfully register.
        The device registry is done manually on this project phase. Please contact the EWF's Ramp up team.

        Source:
            AssetLogic.sol
        Call stack:
            function createAsset() external onlyRole(RoleManagement.Role.AssetAdmin)
            function initLocation ( uint _index, bytes32 _country, bytes32 _region, bytes32 _zip, bytes32 _city, bytes32 _street, bytes32 _houseNumber, bytes32 _gpsLatitude, bytes32 _gpsLongitude ) external isInitialized onlyRole(RoleManagement.Role.AssetAdmin)
            function initGeneral ( uint _index, address _smartMeter, address _owner, AssetType _assetType, Compliance _compliance, uint _operationalSince, uint _capacityWh, bool _active ) external isInitialized userHasRole(RoleManagement.Role.AssetManager, _owner) onlyRole(RoleManagement.Role.AssetAdmin)
        Wait for:
            event LogAssetCreated(address sender, uint id);
            event LogAssetFullyInitialized(uint id);
        TODO: Implement in next releases
        """
        pass


class OriginProducer(OriginV1):
    """
    Green Energy Producer

    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def mint(self, energy: ProducedEnergy) -> dict:
        """
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead( uint _assetId, uint _newMeterRead, bool _smartMeterDown, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown ) external isInitialized onlyAccount(AssetProducingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, bool _smartMeterDown, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
        """
        if not isinstance(energy.value, int):
            raise ValueError('No Produced energy present or in wrong format.')
        if not isinstance(energy.is_meter_down, bool):
            raise ValueError('No Produced energy status present or in wrong format.')
        if not isinstance(energy.previous_hash, str):
            raise ValueError('No Produced hash of last file present or in wrong format.')
        if not isinstance(energy.co2_saved, int):
            raise ValueError('No Produced co2 present or in wrong format.')
        if not isinstance(energy.is_co2_down, bool):
            raise ValueError('No Produced co2 status present or in wrong format.')

        receipt = self.send_raw('producer', 'saveSmartMeterRead', self.asset_id, energy.value,
                                energy.is_meter_down, energy.previous_hash.encode(),
                                energy.co2_saved, energy.is_co2_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def last_hash(self):
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call('producer', 'getLastSmartMeterReadFileHash', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def last_state(self):
        """
        Get complete state of initiated Asset
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetGeneral(uint _assetId)
                external
                constant
                returns(
                    address _smartMeter,
                    address _owner,
                    uint _operationalSince,
                    uint _lastSmartMeterReadWh,
                    bool _active,
                    bytes32 _lastSmartMeterReadFileHash
                    )
        """
        # TODO store with names keys
        receipt = self.call('producer', 'getAssetGeneral', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt


class OriginConsumer(OriginV1):
    """
    Green Energy Consumer

    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def mint(self, energy: ConsumedEnergy) -> dict:
        """
        Source:
            AssetConsumingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, bool _smartMeterDown) external isInitialized onlyAccount(AssetConsumingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesUsedForWh, bool _smartMeterDown);
        """
        if not isinstance(energy.value, int):
            raise ValueError('No Produced energy present or in wrong format.')
        if not isinstance(energy.is_meter_down, bool):
            raise ValueError('No Produced energy status present or in wrong format.')
        if not isinstance(energy.previous_hash, str):
            raise ValueError('No Produced hash of last file present or in wrong format.')
        receipt = self.send_raw('consumer', 'saveSmartMeterRead', self.asset_id, energy.value,
                                energy.previous_hash.encode(), energy.is_meter_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def last_hash(self):
        """
        Get last file hash registered from consumer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call('consumer', 'getLastSmartMeterReadFileHash', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def last_state(self):
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetGeneral(uint _assetId)
                external
                constant
                returns (
                    address _smartMeter,
                    address _owner,
                    uint _operationalSince,
                    uint _capacityWh,
                    bool _maxCapacitySet,
                    uint _lastSmartMeterReadWh,
                    uint _certificatesUsedForWh,
                    bool _active,
                    bytes32 _lastSmartMeterReadFileHash
                    )
        """
        receipt = self.call('consumer', 'getAssetGeneral', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt
