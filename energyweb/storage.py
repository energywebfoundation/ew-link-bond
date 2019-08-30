"""
__Storage__ supports EWF's Origin release A log storage, designed to record a sequence of _off-chain_ files by updating the previous file contents SHA hash with the next. It is particularly useful to enforce data integrity, by comparing the sequence of raw smart-energy_meter readings with the sequence registered _on-chain_.
"""
import os
import json
import pickle
import hashlib
import datetime
import base58

from energyweb.interfaces import Serializable


class ChainFile:
    """
    List element
    """
    def __init__(self, file: str, timestamp: datetime.datetime):
        self.file = file
        self.timestamp = timestamp


class ChainLink:
    """
    List link
    """
    def __init__(self, data: ChainFile, last_link: object):
        self.data = data
        self.last_link = last_link

    def __next__(self):
        return self.last_link


class OnDiskChain:
    """
    Saves a pickle with the data in chain format.
    """
    def __init__(self, chain_file_name: str, path_to_files: str):
        """
        :param chain_file_name:
        :param path_to_files:
        """
        self.chain_file = os.path.join(path_to_files, chain_file_name)
        self.path = path_to_files
        os.makedirs(path_to_files, exist_ok=True)
        if not os.path.exists(self.chain_file):
            self.__memory = None
            return
        try:
            self.__memory = pickle.load(open(self.chain_file, 'rb'))
        except EOFError:
            self.__memory = None

    @property
    def chain(self) -> ChainLink:
        return self.__memory

    @chain.setter
    def chain(self, chain_link: ChainLink):
        if chain_link is not None:
            raise AttributeError
        self._chain_append(chain_link)

    def add_to_chain(self, data: Serializable) -> str:
        """
        Add new file to chain.
        :param data: Data to store
        :return: File name string
        """
        data_file_name = self._save_file(data)
        chain_data = ChainFile(data_file_name, datetime.datetime.now())
        new_link = ChainLink(data=chain_data, last_link=self.chain)
        self._chain_append(new_link)
        self._save_memory()
        return data_file_name

    def get_last_hash(self) -> str:
        """
        Get hash of the last chain file.
        :return: Base58 hash string
        """
        if self.chain:
            # sha3 = hashlib.sha3_256()
            sha3 = hashlib.sha1()
            sha3.update(open(self.chain.data.file, 'rb').read())
            base58_digest = base58.b58encode(sha3.digest())
            return 'Qm' + base58_digest.decode()
        else:
            return '0x0'

    def _chain_append(self, chain_link: ChainLink):
        self.__memory = chain_link
        self._save_memory()

    def _save_memory(self):
        pickle.dump(self.__memory, open(self.chain_file, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    def _save_file(self, data):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file_name_mask = os.path.join(self.path, '%Y-%m-%d-%H:%M:%S.json')
        file_name = datetime.datetime.now().strftime(file_name_mask)
        with open(file_name, 'w+') as file:
            json.dump(data.to_dict(), file)
        return file_name
