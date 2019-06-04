import energyweb
import datetime

class MyTask(energyweb.Task):
    """
    Example Task
    """

    def coroutine(self):
        print('Task {}: {}\n'.format(self.interval, datetime.datetime.now()))


class MyApp(energyweb.App):
    """
    Example Application
    """

    def prepare(self):
        print('{} Prepared'.format(self.__class__.__name__))

    def configure(self):
        t1 = MyTask(interval=energyweb.LifeCycle.FIVE_SECONDS)
        t2 = MyTask(interval=energyweb.LifeCycle.ONE_MINUTE, is_eager=False)
        [self.add_task(t) for t in [t2, t1]]

    def finish(self):
        print('{} Finished'.format(self.__class__.__name__))


app = MyApp()

"""
Test loop
"""
if __name__ == '__main__':
    app.run()