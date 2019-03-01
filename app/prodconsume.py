#!/usr/bin/env python

import asyncio
import datetime
import time
import energyweb
import urllib
import json

from energyweb.oldconfig import parse_bulk

class MyTask(energyweb.Task):
    def main(self, duration, asset, asset_type):
        running = True
        while running:
            if duration == 0:
                running = True
            else:
                duration -= 1
                if duration == 0:
                    running = False
            print(asset.name, end='', flush=True)
            time.sleep(1)
        return False

    def log_measured_energy(self) -> (energyweb.EnergyData, energyweb.EnergyData):
        """
        Try to reach the meter and logs the measured energy.
        """
        success_msg = '[SUCCESS] {} watts - block # {}'
        error_msg = '[FAIL] energy meter: {} - stack: {}'
        try:
            raw_energy = self.asset.meter.read_state()
            energy = self.__transform(raw_energy)
            tx_receipt = self.asset.asset.mint(energy)
            block_number = str(tx_receipt['blockNumber'])
            self.console.info(success_msg.format(raw_energy, block_number))
            return raw_energy, energy
        except Exception as e:
            self.error_log.exception(error_msg.format(self.asset.meter.__class__.__name__, e))
            self.console.warning('[FAIL] is unreachable.')

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
        configuration_file = json.load(open('app/config.json'))
        bulk_configuration = parse_bulk(configuration_file)
        for production_asset in bulk_configuration.production:
            mytask = MyTask(polling_interval=datetime.timedelta(seconds=1))
            self.add_task(mytask, 0, production_asset, 'production')

myapp = MyApp()
myapp.run()
