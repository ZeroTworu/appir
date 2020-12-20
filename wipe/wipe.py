import abc
import random
import time
from threading import Lock, Thread

from wipe.appir import Appir
from wipe.managers import StructureExceptionHandler
from wipe.params import WipeParams
from wipe.patches import patch_http_connection_pool


class WipeStrategy(Appir):

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

    def re_run(self):
        self.users = {}
        self.opened_new_tab = False
        self._init_driver()
        self.run_strategy()

    @property
    def check_max_users(self):
        return len(self.users) >= self._max_users or self._max_users == 0

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


class FillRoomStrategy(WipeStrategy):

    max_timeout = 1.5

    description = 'Попытка заполнить комнату до отказа'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.mutex = Lock()
        self.need_check = True
        self.check_thread = Thread(target=self.check_thread, name='Control ban thread')
        self.check_thread.start()

    def run_strategy(self):
        with self.seh:
            self._run_strategy()

    def _run_strategy(self):
        while self.is_working:
            self.mutex.acquire()
            self.need_check = self.enter_room(room_url=self.room_url)
            self.mutex.release()
            time.sleep(self.max_timeout)
            if not self.need_check or self.check_max_users:
                self.is_waiting_ban = True
                self._logger.warning('Room %s fool, waiting for bans...', self.room_url)
                self.wait_ban()

    def check_thread(self):
        while self.is_need_thread:
            self.mutex.acquire()
            self.check_and_handle_ban()
            self.mutex.release()
            time.sleep(0.5)

    @property
    def is_need_thread(self):
        return not self.is_waiting_ban and self.need_check and self.is_working

    def _ban_callback(self, *args, **kwargs):
        self.is_waiting_ban = False
        self.need_check = True


class YouTubeStrategy(WipeStrategy):
    description = 'Постоянно заходит рандом и включает ютуб'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_link = None
        self.links = None

    def run_strategy(self):
        with self.seh:
            self._run_strategy()

    def _run_strategy(self):
        self.youtube_link = self.params.get('link')
        youtube_file = self.params.get('file', None)
        if youtube_file is not None:
            self._parse_youtube_file(youtube_file)

        while self.is_working:
            wait_time = random.randint(5, 20)
            self.enter_room(room_url=self.room_url)
            if bool(self.users):
                self._start_youtube()

                self._logger.warning('Youtube %s started wait %d seconds...', self.youtube_link, wait_time)
                time.sleep(wait_time)

                self.try_stop_youtube()
                self.exit_room()
            else:
                self._logger.info('Possible room is fool, waiting 1 min')
                time.sleep(self.one_minute_timeout)

    def _ban_callback(self, *args, **kwargs):
        raise NotImplementedError

    def _start_youtube(self):
        if self.links is not None:
            self.youtube_link = random.choice(self.links)
            self.start_youtube(self.youtube_link)
        else:
            self.start_youtube(self.youtube_link)

    def _parse_youtube_file(self, file):
        with open(file, 'r') as read:
            self.links = read.readlines()


class EnterExitStrategy(WipeStrategy):

    description = 'Стратегия заёба, рандом заходит-выходит (эффективно с fake-media)'

    def run_strategy(self):
        with self.seh:
            self._run_strategy()

    def _run_strategy(self):
        while self.is_working:
            wait_time = random.randint(1, 5)
            self.enter_room(room_url=self.room_url)
            self._logger.info('Entered at %s', self.room_url)
            if self.check_max_users:
                self._logger.info('Max users, now wait %d', wait_time)
                time.sleep(wait_time)
                self.exit_room()

    def _ban_callback(self):
        raise NotImplementedError
