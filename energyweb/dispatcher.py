"""
Asynchronous event watcher loop
"""
import asyncio
import datetime
import time
import concurrent


class Task:
    """
    Tasks are routines that run from time to time respecting an interval and spawn coroutines.
    These routines may only execute if a trigger condition is fired.
    """
    def __init__(self, polling_interval: datetime.timedelta, eager: bool = False):
        """
        :param polling_interval: in seconds
        """
        self.polling_interval = polling_interval
        self.eager = eager

    def prepare(self):
        """
        Perform steps required prior to running the main task
        run exactly once
        """

    def main(self) -> bool:
        """
        The main task
        run until it returns False
        """

    def finish(self) -> None:
        """
        Perform steps required after running the main task
        run exactly once
        """

    def run(self, *args):
        """
        run all steps of the task
        """
        self.prepare()
        while self.main(*args) is True:
            # sleep yields to the thread scheduler
            time.sleep(self.polling_interval.total_seconds())
        self.finish()


class EventLoop:
    """
    Delegate and run a set of Tasks in loop that handles I/O or blocking with async calls.
    https://en.wikipedia.org/wiki/Event_loop
    https://docs.python.org/3/library/asyncio.html
    """
    def __init__(self):
        self.task_list = []
        self.started_tasks = []

    def add_task(self, task: Task, *args):
        """
        add task to event task list
        """
        if not task:
            raise Exception('Please add a Task type with callable task named method.')
        self.task_list.append((task, args))

    async def run(self):
        """
        execute all tasks in task list in their own thread
        """
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

    def configure(self):
        """
        Overwrite this method to implement application logic
        add tasks here
        """
        raise NotImplementedError

    def run(self):
        """
        Call the overwritten configure and run the eventLoop
        """
        self.configure()
        # python 3.6
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(super().run())
        asyncio.run(super().run())
