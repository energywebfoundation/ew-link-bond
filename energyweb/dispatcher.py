"""
Asynchronous event watcher loop
"""
import asyncio
import datetime


class Task:
    """
    Tasks are routines that run from time to time respecting an interval and spawn coroutines.
    These routines may only execute if a trigger condition is fired.
    """
    def __init__(self, queue: {str: asyncio.Queue}, polling_interval: datetime.timedelta = None, eager: bool = False, run_forever: bool = True):
        """
        :param polling_interval: in seconds
        :param queue: app asyncio queues for messages exchange between threads
        :param eager: if main waits polling time first or is eager to start
        """
        self.polling_interval = polling_interval
        self.queue = queue
        self.run_forever = run_forever
        self.eager = eager

    async def _prepare(self):
        """
        Perform steps required prior to running the main task
        run exactly once
        """
        raise NotImplementedError

    async def _main(self, *args):
        """
        The main task
        """
        raise NotImplementedError

    async def _finish(self):
        """
        Perform steps required after running the main task
        run exactly once
        """
        raise NotImplementedError

    def _handle_exception(self, e: Exception):
        """
        Handle exceptions when they occur
        """
        raise NotImplementedError

    async def run(self, *args):
        """
        run all steps of the task
        """
        async def main_loop():
            if self.polling_interval and not self.eager:
                await asyncio.sleep(self.polling_interval.total_seconds())
            await self._main(*args)
            if self.polling_interval and self.eager:
                await asyncio.sleep(self.polling_interval.total_seconds())
        try:
            await self._prepare()
            try:
                await main_loop()
                while self.run_forever:
                    await main_loop()
            except Exception as e:
                self._handle_exception(e)
            finally:
                await self._finish()
                if self.run_forever:
                    await self.run(*args)
        except Exception as e:
            self._handle_exception(e)


class App:
    """
    General application abstraction
    """
    def __init__(self):
        self.tasks: [asyncio.tasks] = []
        self.queue: {str: asyncio.Queue} = {}
        self.loop = asyncio.get_event_loop()
        self._configure()

    def _configure(self):
        """
        Configuration phase of the app.
        """
        raise NotImplementedError

    def _clean_up(self):
        """
        Overwrite this method to implement clean up logic like closing sockets and streams.
        """
        raise NotImplementedError

    def _handle_exception(self, e: Exception):
        """
        Handle exceptions when they occur
        """
        raise NotImplementedError

    def _register_task(self, task: Task, *args):
        """
        Add task to be executed in run time
        """
        if not task:
            raise Exception('Please add a Task type with callable task named method.')
        self.tasks.append((task, args))

    def _register_queue(self, queue_id: str, max_size: int = 0):
        """
        Creates a new asyncio Queue for messages exchange between threads
        :param queue_id: Name of queue index
        :param max_size: Maximum number of messages
        """
        self.queue[queue_id] = asyncio.Queue(maxsize=max_size)

    def run(self):
        """
        execute all tasks in task list in their own thread
        """
        try:
            self.loop.run_until_complete(asyncio.gather(*[task.run(*args) for task, args in self.tasks]))
        except KeyboardInterrupt:
            self._clean_up()
            if self.loop.is_running():
                self.loop.close()
        except Exception as e:
            self._handle_exception(e)
        finally:
            self._clean_up()
