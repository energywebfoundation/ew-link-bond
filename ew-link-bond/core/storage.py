"""
Data Access Object
https://en.wikipedia.org/wiki/Data_access_object
"""
import os
import json
import pickle
import hashlib
import datetime

from core import LocalFileData, base58


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


class DiskStorage:
    """
    Saves a pickle with the data in chain format.
    """

    def __init__(self, chain_file_name: str, path_to_files: str):
        """
        :param chain_file_name:
        :param path_to_files:
        """
        self.chain_file = path_to_files + chain_file_name
        self.path = path_to_files
        if not os.path.exists(path_to_files):
            os.makedirs(path_to_files)
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
        self.__chain_append(chain_link)

    def add_to_chain(self, data: LocalFileData) -> str:
        """
        Add new file to chain.
        :param data: Data to store
        :return: Base58 hash string
        """
        data_file_name = self.__save_file(data)
        chain_data = ChainFile(data_file_name, datetime.datetime.now())
        new_link = ChainLink(data=chain_data, last_link=self.chain)
        self.__chain_append(new_link)
        self.__save_memory()
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
            return 'Qm' + base58_digest
        else:
            return '0x0'

    def __chain_append(self, chain_link: ChainLink):
        self.__memory = chain_link
        self.__save_memory()

    def __save_memory(self):
        pickle.dump(self.__memory, open(self.chain_file, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    def __save_file(self, data):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file_name_mask = self.path + '%Y-%m-%d-%H:%M:%S.json'
        file_name = datetime.datetime.now().strftime(file_name_mask)
        with open(file_name, 'w+') as file:
            json.dump(data.to_dict(), file)
        return file_name
