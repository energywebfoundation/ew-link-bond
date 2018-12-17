"""
General & energy related data input interfaces
"""
import time

from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from web3.utils.filters import Filter

from energyweb import ExternalData, EnergyUnit, RawEnergyData, RawCarbonEmissionData, Energy, BlockchainClient


class ExternalDataSource:
    """
    Interface to enforce correct return type and standardized naming
    """
    def read_state(self, *args, **kwargs) -> ExternalData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: ExternalData
        """
        raise NotImplementedError


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


class CarbonEmissionDataSource(ExternalDataSource):
    """
    Carbon emission endpoint data interface
    """

    def read_state(self, *args, **kwargs) -> RawCarbonEmissionData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: RawCarbonEmissionData
        """


class EVMSmartContractClient(BlockchainClient):
    """
    General EVM based blockchain client smart contract integration.
    Tested on:
        - https://github.com/paritytech/parity
        - https://github.com/energywebfoundation/energyweb-client
    """

    def __init__(self, credentials: tuple, contracts: dict, client_url: str, max_retries: int, retry_pause: int):
        """
        :param credentials: Network credentials ( address, password )
        :param contracts: Contracts structure containing abi and bytecode keys.
        :param client_url: URL like address to the blockchain client api.
        :param max_retries: Software will try to connect to provider this amount of times
        :param retry_pause: Software will wait between reconnection trials this amount of seconds
        """
        self.MAX_RETRIES = max_retries
        self.SECONDS_BETWEEN_RETRIES = retry_pause
        self.w3 = Web3(HTTPProvider(client_url))
        self.credentials = credentials
        self.contracts = contracts

    def is_synced(self) -> bool:
        """
        Simple algorithm to check if the blockchain client is synced to the latest block.
        :return: Is synced true or false
        """
        synced_block = str(self.w3.eth.blockNumber)
        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)
        return synced_block == latest_block

    def send(self, contract_name: str, method_name: str, *args) -> dict:
        """
        Sends a regular transaction to call a smart-contract method. This requires the user have the keys previously
        imported to the blockchain client and to accept the transaction on Metamask or on the client's user interface.
        :param contract_name: Contract key as in the contracts list used to instantiate this class.
        :param method_name: Method name as in the contract abi.
        :param args: Arguments passed when calling the method. Must be in the same order as in the abi.
        :return: The transaction receipt after mining is confirmed.
        """
        # TODO: Check for more elegant way of verifying the tx receipt
        if not self.is_synced():
            raise ConnectionError('Client is not synced to the last block.')
        self.w3.personal.unlockAccount(account=self.w3.toChecksumAddress(self.credentials[0]),
                                       passphrase=self.credentials[1])
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        tx_hash = getattr(contract_instance, method_name)(*args, transact={
            'from': self.w3.toChecksumAddress(self.credentials[0])})
        if not tx_hash:
            raise ConnectionError('Transaction was not sent.')
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt

    def call(self, contract_name: str, method_name: str, *args) -> dict:
        """
        Calls a smart-contract method without sending a transaction. Suitable for read-only operations.
        :param contract_name: Contract key as in the contracts list used to instantiate this class.
        :param method_name: Method name as in the contract abi.
        :param args: Arguments passed when calling the method. Must be in the same order as in the abi.
        :return: The transaction receipt after mining is confirmed.
        """
        if not self.is_synced():
            raise ConnectionError('Client is not synced to the last block.')
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        return getattr(contract_instance, method_name)(*args)

    def send_raw(self, contract_name: str, method_name: str, *args) -> dict:
        """
        Sends a raw transaction to call a smart-contract method.
        First it creates the transaction, then fetches the account tx count - to avoid repetition attacks,
        determines gas price, signs it, and finally sends it to the blockchain client.
        :param contract_name: Contract key as in the contracts list used to instantiate this class.
        :param method_name: Method name as in the contract abi.
        :param args: Arguments passed when calling the method. Must be in the same order as in the abi.
        :return: The transaction receipt after mining is confirmed.
        """
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'])

        if not self.is_synced():
            raise ConnectionError('Client is not synced to the last block.')

        nonce = self.w3.eth.getTransactionCount(account=self.w3.toChecksumAddress(self.credentials[0]))
        transaction = {
            'from': self.w3.toChecksumAddress(self.credentials[0]),
            'gas': 400000,
            'gasPrice': self.w3.toWei('0', 'gwei'),
            'nonce': nonce,
        }
        tx = getattr(contract_instance.functions, method_name)(*args).buildTransaction(transaction)
        private_key = bytearray.fromhex(self.credentials[1])
        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        if not tx_hash:
            raise ConnectionError('Transaction was not sent.')
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt

    def create_event_filter(self, contract_name: str, event_name: str, block_count: int = 1000) -> Filter:
        """
        Create Filter on the client, the client must have the option enabled or it might fail.
        :param contract_name: Contract key as in the contracts list used to instantiate this class.
        :param event_name: Like written in the abi
        :param block_count: Number of blocks prior to the latest to start filtering from
        :return: Filter
        """
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'])
        latest_block = self.w3.eth.getBlock('latest')
        return getattr(contract_instance.events, event_name)().createFilter(fromBlock=latest_block.number - block_count)

    def create_event_trigger(self, contract_name: str, event_name: str, block_count: int = 1000) -> dict:
        """
        Todo: Fix this to get the blocks and check for new events, demands memory or persistence
        Create Filter on the client, the client must have the option enabled or it might fail.
        :param contract_name: Contract key as in the contracts list used to instantiate this class.
        :param event_name: Like written in the abi
        :param block_count: Number of blocks prior to the latest to start filtering from
        :return: Filter
        """
        usn_filter = self.create_event_filter(contract_name=contract_name, event_name=event_name, block_count=block_count)
        event_logs = usn_filter.get_all_entries()
        # sessionId = Web3.toHex(event_logs[-1]['transactionHash'])
        return event_logs

    def mint(self, energy: Energy) -> dict:
        """
        Mint the measured energy in the blockchain smart-contract
        """
        raise NotImplementedError
