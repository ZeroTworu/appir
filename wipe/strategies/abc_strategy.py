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

        self.params = params.others_params
        self.room_url = params.room_url
        self._max_users = params.max_users
        self._is_waiting_ban = False

        super().__init__(params)

        self.seh = StructureExceptionHandler(
            logger=params.logger,
            exc_callback=self.re_run,
            normal_callback=self.driver.quit,
        )

    @property
    def check_max_users(self):
        return len(self.users) >= self._max_users and self._max_users != 0

    def re_run(self):
        self._logger.warning('Crash! Will restart driver...')
        self.driver.quit()
        self._logger.info('Old driver stop')
        self.users = {}
        self._opened_new_tab = False
        self._logger.info('Init new driver...')
        self._init_driver()
        self.run()

    def run(self):
        with self.seh:
            self.run_strategy()

    def wait_ban(self):
        while self._is_waiting_ban and self.is_working:
            self.check_and_handle_ban(self._ban_callback)

    def stop_wipe(self):
        self.is_working = False
        time.sleep(self.max_timeout)
        self.driver.quit()

    @abc.abstractmethod
    def _ban_callback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_strategy(self):
        raise NotImplementedError
