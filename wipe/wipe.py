import abc
import logging
import random
import time

from wipe.appir import Appir


class WipeStrategy(object):

    def __init__(
        self,
        room_url: str,
        browser: str = 'firefox',
        headless: bool = True,
        knock: bool = False,
    ):
        self.appir = Appir(headless=headless, browser=browser, knock=knock)
        self.params = {}
        self.room_url = room_url
        self.is_waiting_ban = False

    def set_params(self, params: dict = None):
        self.params = params

    def wait_ban(self):
        while self.is_waiting_ban:
            self.appir.check_ban(self._ban_callback)

    @abc.abstractmethod
    def _ban_callback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_strategy(self):
        raise NotImplementedError


class FillRoomStrategy(WipeStrategy):

    max_timeout = 1.5

    def run_strategy(self):
        while True:
            self.appir.enter_room(room_url=self.room_url)
            if self.appir.is_fool:

                self.appir.users.pop(self.appir.driver.window_handles[-1])
                self.appir.driver.close_tab()
                self.is_waiting_ban = True

                logging.info('Room %s fool, waiting for bans...', self.room_url)
                self.wait_ban()

    def _ban_callback(self, *args, **kwargs):
        self.is_waiting_ban = False


class YouTubeStrategy(WipeStrategy):
    links = None

    def run_strategy(self):
        youtube_link = self.params.get('link')
        youtube_file = self.params.get('file', None)
        if youtube_file is not None:
            self._parse_youtube_file(youtube_file)

        while True:
            wait_time = random.randint(5, 20)
            self.appir.enter_room(room_url=self.room_url)

            if self.links is not None:
                youtube_link = random.choice(self.links)
                self.appir.start_youtube(youtube_link)
            else:
                self.appir.start_youtube(youtube_link)

            logging.info('Youtube %s started wait %d seconds...', youtube_link, wait_time)
            time.sleep(wait_time)

            self.appir.try_stop_youtube()
            self.appir.exit_room()

    def _ban_callback(self, *args, **kwargs):
        raise NotImplementedError

    def _parse_youtube_file(self, file):
        with open(file, 'r') as read:
            self.links = read.readlines()  # noqa: WPS601
