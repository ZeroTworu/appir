import abc
import logging
import random
import time

from wipe.appir import Appir
from wipe.params import WipeParams


class WipeStrategy(Appir):

    description = 'DESCRIPTION WHERE'

    def __init__(self, params: WipeParams):
        self.params = params.others_params
        self.room_url = params.room_url
        self.is_waiting_ban = False
        if params.logger is not None:
            self.logger = params.logger
        else:
            self.logger = logging.getLogger(__name__)

        super().__init__(params)

    def wait_ban(self):
        while self.is_waiting_ban:
            self.check_and_handle_ban(self._ban_callback)

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
        while True:
            self.enter_room(room_url=self.room_url)
            if self.is_fool:

                self.users.pop(self.driver.window_handles[-1])
                self.driver.close_tab()
                self.is_waiting_ban = True

                self.logger.info('Room %s fool, waiting for bans...', self.room_url)
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

        while True:
            wait_time = random.randint(5, 20)
            self.enter_room(room_url=self.room_url)

            if self.links is not None:
                youtube_link = random.choice(self.links)
                self.start_youtube(youtube_link)
            else:
                self.start_youtube(youtube_link)

            self.logger.info('Youtube %s started wait %d seconds...', youtube_link, wait_time)
            time.sleep(wait_time)

            self.try_stop_youtube()
            self.exit_room()

    def _ban_callback(self, *args, **kwargs):
        raise NotImplementedError

    def _parse_youtube_file(self, file):
        with open(file, 'r') as read:
            self.links = read.readlines()  # noqa: WPS601
