import os
import logging
import colorlog


class Logger:
    """
    Instantiate loggers for general purpose
    """

    def __init__(self, log_name: str, store: str = None, enable_debug: bool = False):
        """
        :param log_name: File name for the log. Will create log entries and file name ie. my_app.log
        :param store: Path to folder where the log files will be stored in disk. Please note that disk can get full and prevent OS boot.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """

        tty_handler = colorlog.StreamHandler()
        tty_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

        console = colorlog.getLogger(log_name)
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(process)d][%(levelname)s]%(message)s')
        if store:
            if not os.path.exists(store):
                os.makedirs(store)
            file_handler = logging.FileHandler(os.path.join(store, f'{log_name}.log'))
            file_handler.setFormatter(formatter)
            console.addHandler(file_handler)
        console.addHandler(tty_handler)
        console.setLevel(logging.DEBUG)
        error_log = None
        if enable_debug:
            if not store:
                raise Exception('Needs storage path in store parameter defined.')
            error_log = logging.getLogger(log_name + '.error')
            error_file_handler = logging.FileHandler(os.path.join(store, f'{log_name}.error.log'))
            error_file_handler.setFormatter(formatter)
            error_log.addHandler(error_file_handler)
            error_log.setLevel(logging.WARNING)

        self.store = store
        self.console = console
        self.error_log = error_log
        self.enable_debug = enable_debug
