"""Global logger object."""

import os
from logging.handlers import TimedRotatingFileHandler
import logging

LOG_DIR = os.getenv('LOG_DIR')
LOG_LEVEL = os.getenv('LOG_LEVEL')


class GatewayLogger():
    """A representation of a logging object."""

    def __init__(self, file: str, root=True):
        """Initialisation."""
        self.log_name = os.path.basename(file).replace('.py', '.log')

        if root:
            self._logger = logging.getLogger()
        else:
            self._logger = logging.getLogger(self.log_name.replace('.log', ''))

        self._logger.setLevel(LOG_LEVEL)

        self.logger_filename = os.path.join(
            LOG_DIR,
            self.log_name
        )

        file_handler = TimedRotatingFileHandler(
            self.logger_filename,
            when='midnight',
            interval=1
        )

        file_handler.suffix = "%Y%m%d"

        log_format = logging.Formatter(
            '%(name)s - %(asctime)s - %(message)s', '%d-%b-%y %H:%M:%S'
        )

        file_handler.setFormatter(log_format)

        self._logger.addHandler(file_handler)

    @property
    def logger(self):
        """Return the loging object."""
        return self._logger
