import logging
import os

import colorlog

from energyweb import Energy, RawEnergyData
from energyweb.config import EnergyAssetConfiguration


class Logger:
    """
    Instantiate loggers for general purpose
    """

    def __init__(self, log_name: str, store: str = None, enable_debug: bool = False):
        """
        :param log_name: File name for the log. Will create log entries and file name ie. my_app.log
        :param store: Path to folder where the log files will be stored in disk. Please note that it can get full.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """

        tty_handler = colorlog.StreamHandler()
        tty_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

        console = colorlog.getLogger(log_name)
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(process)d][%(levelname)s]%(message)s')
        if store:
            if not os.path.exists(store):
                os.makedirs(store)
            file_handler = logging.FileHandler(store + log_name + '.log')
            file_handler.setFormatter(formatter)
            console.addHandler(file_handler)
        console.addHandler(tty_handler)
        console.setLevel(logging.DEBUG)
        error_log = None
        if enable_debug:
            if not store:
                raise Exception('Needs storage path in store parameter defined.')
            error_log = logging.getLogger(log_name + '.error')
            error_file_handler = logging.FileHandler(store + log_name + '.error.log')
            error_file_handler.setFormatter(formatter)
            error_log.addHandler(error_file_handler)
            error_log.setLevel(logging.WARNING)

        self.store = store
        self.console = console
        self.error_log = error_log
        self.enable_debug = enable_debug


class EnergyLogger(Logger):
    """
    Energy data logger implementation.
    Read configuration, reach the provided smart meters, send to blockchain, log the results.
    """
    def __init__(self, asset: EnergyAssetConfiguration, store: str = None, enable_debug: bool = False):
        """
        :param asset: Consumer configuration class instance
        :param store: Path to folder where the log files will be stored in disk. Please note that it can get full.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        self.asset = asset
        super().__init__(log_name=asset.name, store=store, enable_debug=enable_debug)

    def log_configuration(self):
        """
        Outputs the logger configuration
        """
        message = '[CONFIG] name: {} - energy meter: {}'
        if self.store and self.enable_debug:
            self.console.debug('[CONFIG] path to logs: {}'.format(self.store))
        self.console.debug(message.format(self.asset.name, self.asset.meter.__class__.__name__))

    def log_measured_energy(self) -> (RawEnergyData, Energy):
        """
        Try to reach the meter and logs the measured energy.
        """
        success_msg = '[SUCCESS] {} watts - block # {}'
        error_msg = '[FAIL] energy meter: {} - stack: {}'
        try:
            raw_energy = self.asset.meter.read_state()
            energy = self.__transform(raw_energy)
            tx_receipt = self.asset.smart_contract.mint(energy)
            block_number = str(tx_receipt['blockNumber'])
            self.console.info(success_msg.format(raw_energy, block_number))
            return raw_energy, energy
        except Exception as e:
            self.error_log.exception(error_msg.format(self.asset.meter.__class__.__name__, e))
            self.console.warning('[FAIL] is unreachable.')

    def __transform(self, raw_energy: RawEnergyData) -> Energy:
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract.
        """
        raise NotImplementedError
