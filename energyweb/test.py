#!/usr/bin/env python

import energyweb
import datetime

from energyweb.eds.energy_api import BondAPIv1TestDevice1, BondAPIv1TestDevice2


class MyTask(energyweb.Task):
    """
    Example Task
    """

    def coroutine(self):
        print('Task {}: {}\n'.format(self.interval, datetime.datetime.now()))


class TestTask1(energyweb.Task):

    def __init__(self):
        super().__init__(energyweb.LifeCycle.FIVE_SECONDS)

    def coroutine(self):
        logger = energyweb.Logger('Test Task 1')
        d1 = BondAPIv1TestDevice1("base_url", "produced", 0)
        state = d1.read_state()
        logger.console.info('Task {} {}: {} - {}'.format(1, datetime.datetime.now(), state.measurement_epoch, state.energy))


class TestTask2(energyweb.Task):
    def coroutine(self):
        logger = energyweb.Logger('Test Task 1')
        d1 = BondAPIv1TestDevice2("base_url", "produced", 0)
        state = d1.read_state()
        logger.console.info('Task {} {}: {} - {}'.format(2, datetime.datetime.now(), state.measurement_epoch, state.energy))


class MyApp(energyweb.App):
    """
    Example Application
    """

    def prepare(self):
        print('{} Prepared'.format(self.__class__.__name__))

    def configure(self):
        t1 = TestTask1()
        t2 = TestTask2(interval=energyweb.LifeCycle.SEVEN_SECONDS)
        [self.add_task(t) for t in [t2, t1]]

    def finish(self):
        print('{} Finished'.format(self.__class__.__name__))


if __name__ == '__main__':
    app = MyApp()
    app.run()
