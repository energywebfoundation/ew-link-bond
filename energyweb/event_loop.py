"""
Asynchronous watcher event loop threads
"""
import asyncio
from datetime import datetime
from enum import IntEnum


class LifeCycle(IntEnum):
    """
    Data source reading time cycle. Determines the period time is collected.
    """
    FIVE_SECONDS = 5
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
    def __init__(self, interval: LifeCycle, is_eager: bool=True):
        """
        :param interval: in seconds
        :param is_eager: to execute this task right away
        """
        self.interval = interval
        self.is_eager = is_eager

    def trigger_event(self):
        return True

    def coroutine(self) -> None:
        raise NotImplementedError

    async def task(self):
        if self.is_eager:
            if self.trigger_event():
                self.coroutine()
        while True:
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
            raise Exception('Please add a callable function or method.')
        self.task_list.append(asyncio.ensure_future(task.task()))

    def run(self):
        if len(self.task_list) < 1:
            raise Exception('Event loop aborted: Empty task list.')
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.close()


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
        super().run()
        self.finish()


if __name__ == '__main__':

    class MyTask(Task):
        """
        Example Task
        """
        def coroutine(self):
            print('Task {}: {}\n'.format(self.interval, datetime.now()))


    class MyApp(App):
        """
        Example Application
        """
        def prepare(self):
            print('{} Prepared'.format(self.__class__.__name__))

        def configure(self):
            t1 = MyTask(interval=LifeCycle.FIVE_SECONDS)
            t2 = MyTask(interval=LifeCycle.ONE_MINUTE, is_eager=False)
            [self.add_task(t) for t in [t2, t1]]

        def finish(self):
            print('{} Finished'.format(self.__class__.__name__))

    app = MyApp()
    app.run()
