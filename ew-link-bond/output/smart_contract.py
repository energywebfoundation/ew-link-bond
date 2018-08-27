import time

from web3 import HTTPProvider, Web3
from web3.contract import ConciseContract

from core.output import SmartContractClient


class GeneralSmartContractClient(SmartContractClient):
    """
    General EVM based blockchain client smart contract integration.
    Tested:
        - https://github.com/paritytech/parity
        - https://github.com/ethereum/go-ethereum
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

    def check_sync(self) -> bool:
        synced_block = str(self.w3.eth.blockNumber)
        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)
        return synced_block == latest_block

    def send(self, contract_name: str, method_name: str, event_name: str, *args) -> dict:
        # TODO: Events parsing : myContract.events.myEvent().processReceipt(receipt)
        # TODO: Check for more elegant way of verifying the tx receipt
        if not self.check_sync():
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
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        return getattr(contract_instance, method_name)(*args)

    def send_raw(self, contract_name: str, method_name: str, *args) -> dict:
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')

        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract['address']),
            bytecode=contract['bytecode'])

        nonce = self.w3.eth.getTransactionCount(account=self.w3.toChecksumAddress(self.credentials[0]))
        transaction = {
            'from': self.w3.toChecksumAddress(self.credentials[0]),
            'gas': 400000,
            'gasPrice': self.w3.toWei('0', 'gwei'),
            'nonce': nonce,
        }
        tx = getattr(contract_instance.functions, method_name)(*args).buildTransaction(transaction)
        self.w3.eth.enable_unaudited_features()
        private_key = bytearray.fromhex(origin.wallet_pwd)
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
