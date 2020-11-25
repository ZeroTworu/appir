import abc
import logging
import random
import time

import attr
from wipe.appir import Appir


@attr.s
class WipeParams(object):
    room_url: str = attr.ib()
    browser: str = attr.ib(default='firefox')
    headless: bool = attr.ib(default=True)
    knock: bool = attr.ib(default=False)
    fake_media: bool = attr.ib(default=False)
    others_params: dict = attr.ib(default={})


class WipeStrategy(object):

    def __init__(self, params: WipeParams):
        self.appir = Appir(headless=params.headless, browser=params.browser, knock=params.knock)
        self.params = params.others_params
        self.room_url = params.room_url
        self.is_waiting_ban = False

    def wait_ban(self):
        while self.is_waiting_ban:
            self.appir.check_and_handle_ban(self._ban_callback)

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
