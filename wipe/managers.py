import logging
from typing import Callable

from selenium.common.exceptions import TimeoutException


class StructureExceptionHandler(object):

    def __init__(self, logger: logging.Logger = None, exc_callback: Callable = None, normal_callback: Callable = None):
        if logger is None:
            self._logger = logging.getLogger('SEH')
        else:
            self._logger = logger

        self._exc_callback = exc_callback
        self._normal_callback = normal_callback

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        is_exc = exc_type is not None and exc_val is not None and exc_tb is not None

        if is_exc and not isinstance(exc_val, KeyboardInterrupt):
            if isinstance(exc_val, TimeoutException):
                self._logger.warning('Timeout exc')
            else:
                self._logger.exception('Unhandled exception %s', exc_val)
            if self._exc_callback is not None:
                self._exc_callback()
        else:
            self._logger.info('Normal exit')
            if self._normal_callback is not None:
                self._normal_callback()
