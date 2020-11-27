import abc
import random
import time
from threading import Thread
from wipe.appir import Appir
from wipe.params import WipeParams


class WipeStrategy(Appir):

    description = 'DESCRIPTION WHERE'

    def __init__(self, params: WipeParams):
        self.params = params.others_params
        self.room_url = params.room_url
        self.is_waiting_ban = False
        super().__init__(params)

    def wait_ban(self):
        while self.is_waiting_ban and self.is_working:
            self.check_and_handle_ban(self._ban_callback)

    def stop_wipe(self):
        self.driver.quit()
        self.is_working = False

    @abc.abstractmethod
    def _ban_callback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_strategy(self):
        raise NotImplementedError


class FillRoomStrategy(WipeStrategy):

    max_timeout = 1.5

    description = 'Попытка заполнить комнату до отказа'

    def run_strategy(self):
        while self.is_working:
            self.enter_room(room_url=self.room_url)
            if self.is_fool:
                self.users.pop(self.driver.window_handles[-1])
                self.driver.close_tab()
                self.is_waiting_ban = True
                time.sleep(0.5)
                self.logger.warning('Room %s fool, waiting for bans...', self.room_url)
                self.wait_ban()

    def _ban_callback(self, *args, **kwargs):
        self.is_waiting_ban = False


class YouTubeStrategy(WipeStrategy):
    links = None
    description = 'Постоянно заходит рандом и включает ютуб'

    def run_strategy(self):
        youtube_link = self.params.get('link')
        youtube_file = self.params.get('file', None)
        if youtube_file is not None:
            self._parse_youtube_file(youtube_file)

        while self.is_working:
            wait_time = random.randint(5, 20)
            self.enter_room(room_url=self.room_url)

            if self.links is not None:
                youtube_link = random.choice(self.links)
                self.start_youtube(youtube_link)
            else:
                self.start_youtube(youtube_link)

            self.logger.warning('Youtube %s started wait %d seconds...', youtube_link, wait_time)
            time.sleep(wait_time)

            self.try_stop_youtube()
            self.exit_room()

    def _ban_callback(self, *args, **kwargs):
        raise NotImplementedError

    def _parse_youtube_file(self, file):
        with open(file, 'r') as read:
            self.links = read.readlines()  # noqa: WPS601
