"""
Asynchronous event watcher loop
"""
import asyncio
import datetime
import time
import urllib.request, urllib.error
import concurrent

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

    def main(self) -> bool:
        return True

    def finish(self) -> None:
        pass

    def run(self, *args):
        self.prepare()
        while self.main(*args):
            # sleep yields to the thread scheduler
            time.sleep(self.polling_interval.total_seconds())
        self.finish()

class EventLoop:
    """
    Delegate and run a set of Tasks in loop that handles I/O or computational blocking with async calls.
    https://en.wikipedia.org/wiki/Event_loop
    https://docs.python.org/3/library/asyncio.html
    """
    def __init__(self):
        self.task_list = []
        self.started_tasks = []

    def add_task(self, task: Task, *args):
        if not task:
            raise Exception('Please add a Task type with callable task named method.')
        self.task_list.append((task, args))

    async def run(self):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for (task, args) in self.task_list:
                started_task = loop.run_in_executor(pool, task.run, *args)
                self.started_tasks.append(started_task)
            for task in self.started_tasks:
                await task

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
