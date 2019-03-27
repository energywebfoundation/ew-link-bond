#!/usr/bin/env python

import asyncio
import datetime
import time
import energyweb
import urllib


class PrintTask(energyweb.dispatcher.Task):

    async def _finish(self):
        print(f'Task {self.__class__.__name__} finished')

    async def _prepare(self):
        print(f'Task {self.__class__.__name__} prepared')

    def _handle_exception(self, e: Exception):
        print(f'Task {self.__class__.__name__} failed because {e.with_traceback(e.__traceback__)}')

    async def _main(self, duration, character):
        for _ in range(duration):
            print(character, end='', flush=True)
            time.sleep(1)
        print('\n')


class PostManTask(energyweb.dispatcher.Task):

    def __init__(self, queue, send_interval, messages: [str]):
        self.messages = messages
        super().__init__(queue, send_interval, run_forever=False)

    async def _finish(self):
        print(f'Task {self.__class__.__name__} finished')

    async def _prepare(self):
        import random
        random.shuffle(self.messages, random.random)
        print(f'Task {self.__class__.__name__} prepared')

    def _handle_exception(self, e: Exception):
        print(f'Task {self.__class__.__name__} failed because {e.with_traceback(e.__traceback__)}')

    async def _main(self):
        for msg in self.messages:
            await self.queue['mail_box'].put(msg)
            await asyncio.sleep(self.polling_interval.total_seconds())
        raise AttributeError(f'Task {self.__class__.__name__} ended delivering messages.')


class MailCheckerTask(energyweb.dispatcher.Task):

    async def _finish(self):
        print(f'Task {self.__class__.__name__} finished')

    async def _prepare(self):
        print(f'Task {self.__class__.__name__} prepared')

    def _handle_exception(self, e: Exception):
        print(f'Task {self.__class__.__name__} failed because {e.with_traceback(e.__traceback__)}')

    async def _main(self):
        messages = []
        while not self.queue['mail_box'].empty():
            messages.append(self.queue['mail_box'].get_nowait())
        if len(messages) > 0:
            [print(msg) for msg in messages]


class NetworkTask(energyweb.dispatcher.Task):
    """
    Example Task reading and writing network
    """

    def __init__(self, queue, polling_interval):
        self.net = None
        super().__init__(queue, polling_interval, eager=True, run_forever=False)

    def _handle_exception(self, e: Exception):
        print(f'Task {self.__class__.__name__} failed because {e.with_traceback(e.__traceback__)}')

    async def _prepare(self):
        print('Net try open')
        try:
            self.net = urllib.request.urlopen(f'http://localhost:8000')
        except urllib.error.URLError:
            print('Net unavailable')

    async def _main(self):
        if self.net:
            response = self.net.read().decode().strip()
            print(response)
            self.queue['network_status'].put({'online': True})
        else:
            raise urllib.error.URLError('Net Unavailable.')

    async def _finish(self):
        print('Net close')
        await self.queue['network_status'].put({'online': False})

class MyApp(energyweb.dispatcher.App):

    def _handle_exception(self, e: Exception):
        print('==== APP ERROR ====')
        print(f'{e.with_traceback(e.__traceback__)}')

    def _clean_up(self):
        print('==== App finished, cleaning up. ====')

    def _configure(self):
        print('==== App reading configuration ====')
        self._register_queue('mail_box')
        self._register_queue('network_status', 1)
        self._register_task(NetworkTask(self.queue, datetime.timedelta(seconds=20)))
        messages = ['Hello Mike', 'Don\'t forget my bday', 'Have a nice day']
        self._register_task(PostManTask(self.queue, datetime.timedelta(seconds=10), messages))
        self._register_task(MailCheckerTask(self.queue, datetime.timedelta(seconds=20)))
        self._register_task(PrintTask(self.queue, datetime.timedelta(minutes=2)), 3, '>')


if __name__ == '__main__':
    app = MyApp()
    app.run()

