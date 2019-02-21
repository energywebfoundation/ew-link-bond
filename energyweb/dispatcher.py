"""
Asynchronous event watcher loop
"""
import asyncio
from enum import IntEnum


class LifeCycle(IntEnum):
    """
    Data source reading time cycle. Determines the period time is collected.
    """
    FIVE_SECONDS = 5
    SEVEN_SECONDS = 7
    TWENTY_SECONDS = 20
    FORTY_SECONDS = 40
    ONE_MINUTE = 60
    TEN_MINUTES = 600
    THIRTY_MINUTES = 1800
    ONE_HOUR = 3600
    SIX_HOURS = 21600
    TWELVE_HOURS = 43200
    ONE_DAY = 86400


class Task:
    """
    Tasks are routines that run from time to time respecting an interval and spawn sync or async coroutines.
    These routines may only execute if a trigger condition is fired.
    """
    def __init__(self, interval: LifeCycle):
        """
        :param interval: in seconds
        """
        self.interval = interval

    def trigger_event(self):
        return True

    def coroutine(self) -> None:
        raise NotImplementedError

    async def task(self):
        await asyncio.sleep(self.interval.value)
        if self.trigger_event():
            self.coroutine()


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
        self.task_list.append(asyncio.ensure_future(task.task()))

    def run(self):
        if len(self.task_list) < 1:
            raise Exception('Event loop aborted: Empty task list.')
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.close()
