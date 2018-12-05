import logging
import os

import colorlog


class AsyncClientError(EnvironmentError):
    pass


class NoCompilerError(NotImplementedError):
    pass


class AllGasUsedWarning(Warning):
    pass


class Logger:
    """
    Instantiate loggers for general purpose
    """

    def __init__(self, logfiles_folder: str, logfile_file: str, errorlog_file: str, name: str):
        """
        ./tobalaba/
        :param logfiles_folder: Path to folder where the log files will be bundled
        :param logfile_file: File name for the logfile. ie. my_app.log
        :param errorlog_file: File name for the error log. ie. my_app.err.log
        :param name: Name that will appear in the logs to identify the process creating it
        """
        self.name = name
        self.path = logfiles_folder

        tty_handler = colorlog.StreamHandler()
        tty_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file_handler = logging.FileHandler(self.path + logfile_file)
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(process)d][%(levelname)s]%(message)s')
        file_handler.setFormatter(formatter)

        # Default color scheme is 'example'
        console = colorlog.getLogger('example')
        console.addHandler(tty_handler)
        console.addHandler(file_handler)
        console.setLevel(logging.DEBUG)

        error_log = logging.getLogger()
        error_file_handler = logging.FileHandler(self.path + errorlog_file)
        error_file_handler.setFormatter(formatter)
        error_log.addHandler(error_file_handler)
        error_log.setLevel(logging.WARNING)

        self.console = console
        self.error_log = error_log

    def log_results(self, *args, **kwargs):
        raise NotImplementedError
