"""
General external data output interfaces
"""

from core import JSONAble


class DataOutput(JSONAble):
    """
    Data output wrapper
    """
    pass


class LogEntry(DataOutput):
    """
    Standard for logging data
    """

    def __init__(self, epoch, value):
        """
        :param epoch:  Time the value was measured in epoch format
        :param value:  Measured value
        """
        self.epoch = epoch
        self.value = value


class SmartContractClient(DataOutput):
    """
    Ethereum-like smart contracts abstraction
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
