import abc
import time

from wipe.appir import Appir
from wipe.managers import StructureExceptionHandler
from wipe.params import WipeParams
from wipe.patches import patch_http_connection_pool


class AbstractWipeStrategy(Appir):  # noqa:  WPS214

    description = 'DESCRIPTION WHERE'

    def __init__(self, params: WipeParams):
        patch_http_connection_pool(maxsize=100)
        super().__init__(params)

        self.strategy_params = params.others_params
        self._max_users = params.max_users
        self._is_waiting_ban = False

        self.seh = StructureExceptionHandler(
            logger=self._logger,
            exc_callback=self.re_start,
            normal_callback=self.driver.quit,
        )

    @property
    def check_max_users(self):
        return len(self.users) >= self._max_users != 0  # noqa: WPS409

    def re_start(self):
        self.users = {}
        self._opened_new_tab = False

        self._logger.warning('Crash! Will restart driver...')
        self.driver.quit()
        self._logger.info('Old driver stop')
        self._logger.info('Init new driver...')
        self._init_driver()
        self.start()

    def start(self):
        with self.seh:
            self.run_strategy()

    def stop(self):
        self.is_working = False
        time.sleep(self.max_timeout)
        self.driver.quit()
        self._logger.info('Stopped')

    def wait_ban(self):
        while self._is_waiting_ban and self.is_working:
            self.check_and_handle_ban(self._ban_callback)

    @abc.abstractmethod
    def _ban_callback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_strategy(self):
        raise NotImplementedError
