#!/usr/bin/env python

import asyncio
import datetime
import time
import energyweb
import urllib

class MyTask(energyweb.dispatcher.Task):
    def main(self, duration, character):
        for _ in range(duration):
            print(character, end='', flush=True)
            time.sleep(1)
        return False

class NetworkTask(energyweb.dispatcher.Task):
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
        mytask = MyTask(polling_interval=datetime.timedelta(seconds=1))
        networktask = NetworkTask(polling_interval=datetime.timedelta(seconds=5))
        self.add_task(mytask, 5, '>')
        self.add_task(mytask, 8, '<')
        self.add_task(networktask, 1)

myapp = MyApp()
myapp.run()
