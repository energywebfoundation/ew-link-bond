import datetime
import inspect


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


class IntegrationPoint:
    """
    Interface to enforce correct return type and standardized naming
    """
    def read_state(self, *args, **kwargs) -> ExternalData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: ExternalData
        """
        raise NotImplementedError

    def write_state(self, *args, **kwargs) -> ExternalData:
        """
        Establishes a connection to the integration medium and persists data
        :rtype: ExternalData
        """
        raise NotImplementedError


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

    def mint(self, energy: ExternalData) -> dict:
        """
        Mint the measured energy in the blockchain smart-contract
        """
        raise NotImplementedError

