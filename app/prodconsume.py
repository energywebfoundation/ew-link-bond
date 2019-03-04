#!/usr/bin/env python
import calendar
import datetime
import time
import energyweb
import urllib
import json

from energyweb.config import CooV1ConsumerConfiguration, CooV1ProducerConfiguration


class CooGeneralTask(energyweb.Logger, energyweb.Task):

    def __init__(self, task_config: energyweb.config.CooV1Configuration, polling_interval: datetime.timedelta,
                 store: str = None, enable_debug: bool = False):
        """
        :param task_config: Consumer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        self.task_config = task_config
        self.path_to_files = './origin_logs/'
        self.chain_file_name = 'chained_logs'
        self.msg_success = 'minted {} watts - block # {}'
        self.msg_error = 'energy_meter: {} - stack: {}'
        energyweb.Logger.__init__(self, log_name=task_config.name, store=store, enable_debug=enable_debug)
        energyweb.Task.__init__(self, polling_interval=polling_interval, eager=False)

    def main(self, duration: int = 3):
        running = True
        self._log_configuration()
        while running:
            self._log_measured_energy()
            time.sleep(duration)
        return False

    def _log_configuration(self):
        """
        Outputs the logger configuration
        """
        message = '[CONFIG] name: {} - energy energy_meter: {}'
        if self.store and self.enable_debug:
            self.console.debug('[CONFIG] path to logs: {}'.format(self.store))
        self.console.debug(message.format(self.task_config.name, self.task_config.energy_meter.__class__.__name__))

    def _log_measured_energy(self):
        """
        Try to reach the energy_meter and logs the measured energy.
        Wraps the complexity of the data read and the one to be written to the smart-contract
        """
        try:
            # Get the data by accessing the external energy device
            # Storing logs locally
            if self.store:
                local_storage = energyweb.DiskStorage(path_to_files=self.path_to_files,
                                                      chain_file_name=self.chain_file_name)
                last_file_hash = local_storage.get_last_hash() if self.store else '0x0'
                energy_data = self._transform(local_file_hash=last_file_hash)
                if energy_data.is_meter_down:
                    local_chain_file = local_storage.add_to_chain(data=energy_data)
                    self.console.info('{} created'.format(local_chain_file))
            else:
                energy_data = self._transform(local_file_hash='0x0')
            # Logging to the blockchain
            tx_receipt = self.task_config.smart_contract.mint(energy_data)
            block_number = str(tx_receipt['blockNumber'])
            self.console.info(self.msg_success.format(energy_data.to_dict(), block_number))
        except Exception as e:
            self.console.exception(self.msg_error.format(self.task_config.energy_meter.__class__.__name__, e))
            self.console.warning('Smart-contract is unreachable.')

    def _transform(self, local_file_hash: str):
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raise NotImplementedError

    def _fetch_remote_data(self, ip: energyweb.IntegrationPoint) -> (energyweb.ExternalData, bool):
        """
        Tries to reach external device for data.
        Returns smart-contract friendly data and logs error in case of failing.
        :param ip: Energy or Carbon Emission Device
        :return: Energy or Carbon Emission Data, Is device offline flag
        """
        try:
            result = ip.read_state()
            if not issubclass(result.__class__, energyweb.ExternalData):
                raise AssertionError('Make sure to inherit ExternalData when reading data from IntegrationPoint.')
            return result, False
        except Exception as e:
            # TODO debug log self.error_log
            self.console.exception(self.msg_error.format(self.task_config.energy_meter.__class__.__name__, e))
            return None, True


class CooProducerTask(CooGeneralTask):

    def __init__(self, task_config: CooV1ProducerConfiguration, polling_interval: datetime.timedelta, store: str = None,
                 enable_debug: bool = False):
        """
        :param task_config: Producer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        super().__init__(task_config=task_config, polling_interval=polling_interval, store=store,
                         enable_debug=enable_debug)

    def _transform(self, local_file_hash: str) -> energyweb.EnergyData:
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raw_energy, is_meter_down = self._fetch_remote_data(self.task_config.energy_meter)
        if not self.task_config.energy_meter.is_accumulated:
            last_remote_state = self.task_config.smart_contract.last_state()
            raw_energy.energy += last_remote_state[3] # get the fourth element returned from the contract from last_state: uint _lastSmartMeterReadWh
        raw_carbon_emitted, is_co2_down = self._fetch_remote_data(self.task_config.carbon_emission)
        calculated_co2 = raw_energy.energy * raw_carbon_emitted.accumulated_co2
        produced = {
            'value': int(raw_energy.energy),
            'is_meter_down': is_meter_down,
            'previous_hash': local_file_hash,
            'co2_saved': int(calculated_co2),
            'is_co2_down': is_co2_down
        }
        return energyweb.ProducedEnergy(**produced)


class CooConsumerTask(CooGeneralTask):

    def __init__(self, task_config: CooV1ConsumerConfiguration, polling_interval: datetime.timedelta, store: str = None,
                 enable_debug: bool = False):
        """
        :param task_config: Consumer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        super().__init__(task_config=task_config, polling_interval=polling_interval, store=store, enable_debug=enable_debug)

    def _transform(self, local_file_hash: str) -> energyweb.EnergyData:
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raw_energy, is_meter_down = self._fetch_remote_data(self.task_config.energy_meter)
        if not self.task_config.energy_meter.is_accumulated:
            last_remote_state = self.task_config.smart_contract.last_state()
            raw_energy.energy += last_remote_state[3]
        consumed = {
            'value': int(raw_energy.energy),
            'is_meter_down': is_meter_down,
            'previous_hash': local_file_hash,
        }
        return energyweb.ConsumedEnergy(**consumed)


class NetworkTask(energyweb.Task):
    """
    Example Task reading and writing network
    """
    def prepare(self):
        print('Net try open')
        return super().prepare()

    def main(self, number):
        try:
            net = urllib.request.urlopen(f'http://localhost:8000/{number}')
        except urllib.error.URLError:
            print('Net unavailable')
            return True

        response = net.read().decode().strip()
        if response == 'ja':
            print('Here we go', end='')
            for _ in range(3):
                print('.', end='', flush=True)
                time.sleep(1)
            print('')
        elif response == 'stop':
            return False
        return True

    def finish(self):
        print('Net close')
        return super().finish()


class MyApp(energyweb.dispatcher.App):

    def configure(self):
        try:
            app_configuration_file = json.load(open('config.json'))
            app_config = energyweb.config.parse_coo_v1(app_configuration_file)
            interval = datetime.timedelta(seconds=1)
            [self.add_task(CooProducerTask(task_config=producer, polling_interval=interval, store='/tmp/prodconsume/produce')) for producer in app_config.production]
            [self.add_task(CooConsumerTask(task_config=consumer, polling_interval=interval, store='/tmp/prodconsume/consume')) for consumer in app_config.consumption]
        except energyweb.config.ConfigurationFileError as e:
            print(f'Error in configuration file: {e}')
        except Exception as e:
            print(f'Fatal error: {e}')


if __name__ == '__main__':
    myapp = MyApp()
    myapp.run()

"""
    def read_production_data(self, task_config: energyweb., last_hash: str, last_state: dict) -> ProductionFileData:
        input_data_dict = {
            'raw_energy': __fetch_input_data(task_config.energy),
            'raw_carbon_emitted': __fetch_input_data(task_config.carbon_emission),
            'produced': None,
        }
        input_data = ProductionFileData(**input_data_dict)
        co2_saved = input_data.raw_carbon_emitted.accumulated_co2 if input_data.raw_carbon_emitted else 0
        energy = int(input_data.raw_energy.accumulated_power) if input_data.raw_energy else 0
        calculated_co2 = energy * co2_saved
        co2_saved = int(calculated_co2 * pow(10, 3))
        energy = int(energy)
        produced = {
            'energy': energy,
            'is_meter_down': True if input_data.raw_energy is None else False,
            'previous_hash': last_hash,
            'co2_saved': co2_saved,
            'is_co2_down': True if input_data.raw_carbon_emitted is None else False
        }
        input_data.produced = ProducedChainData(**produced)
        return input_data

    def _produce(chain_file, task_config, item) -> bool:
        try:
            production_local_chain = dao.DiskStorage(chain_file, PERSISTENCE)
            last_local_chain_hash = production_local_chain.get_last_hash()
            last_remote_state = task_config.client.last_state(item.origin)
            produced_data = dao.read_production_data(item, last_local_chain_hash, last_remote_state)
            created_file = production_local_chain.add_to_chain(produced_data)
            tx_receipt = task_config.client.mint(produced_data.produced, item.origin)
            class_name = item.energy.__class__.__name__
            data = produced_data.produced
            block_number = str(tx_receipt['blockNumber'])
            msg = '[PROD] energy_meter: {} - {} watts - {} kg of Co2 - block: {}'
            if data.is_meter_down:
                logger.warning(msg.format(class_name, data.energy, data.co2_saved, block_number))
            else:
                logger.info(msg.format(class_name, data.energy, data.co2_saved, block_number))
            return True
        except Exception as e:
            error_log.exception("[BOND][PROD] energy_meter: {} - stack: {}".format(item.energy.__class__.__name__, e))
            return False
"""