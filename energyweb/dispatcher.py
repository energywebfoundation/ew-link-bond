"""
Asynchronous event watcher loop
"""
import asyncio
import datetime
import time
import urllib.request, urllib.error

class Task:
    """
    Tasks are routines that run from time to time respecting an interval and spawn sync or async coroutines.
    These routines may only execute if a trigger condition is fired.
    """
    def __init__(self, polling_interval: datetime.timedelta, eager: bool=False):
        """
        :param polling_interval: in seconds
        """
        self.polling_interval = polling_interval
        self.eager = eager

    def prepare(self):
        pass

    def coroutine(self) -> bool:
        return True

    def finish(self) -> None:
        pass

    async def run(self):
        if self.eager:
            self.coroutine()

        while True:
            await asyncio.sleep(self.polling_interval.total_seconds())
            # stop loop if task returned false
            if not self.coroutine():
                self.finish()
                break

class EventLoop:
    """
    Delegate and run a set of Tasks in loop that handles I/O or computational blocking with async calls.
    https://en.wikipedia.org/wiki/Event_loop
    https://docs.python.org/3/library/asyncio.html
    """
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.task_list = []

    def add_task(self, task: Task):
        if not task:
            raise Exception('Please add a Task type with callable task named method.')
        self.task_list.append(asyncio.create_task(task.run()))
        self.loop.run_forever()

    async def run(self):
        await asyncio.gather(*self.task_list)

class App(EventLoop):
    """
    General application abstraction
    """

    def prepare(self):
        pass

    def configure(self):
        raise NotImplementedError

    def finish(self):
        pass

    def run(self):
        self.prepare()
        self.configure()
        asyncio.run(super().run())
        self.finish()

