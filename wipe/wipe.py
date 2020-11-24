import abc
import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException
from wipe.appir import Appir


class WipeStrategy(object):

    def __init__(self, room_url: str, params: dict = None, headless: bool = True, knock: bool = False):
        self.appir = Appir(headless=headless, knock=knock)
        self.params = params
        self.room_url = room_url
        self.is_waiting_ban = False

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

    def run_strategy(self):
        while True:
            self.appir.enter_room(room_url=self.room_url)
            if self._is_fool:
                self.is_waiting_ban = True
                logging.info('Room %s fool, waiting for bans...', self.room_url)
                self.wait_ban()

    @property
    def _is_fool(self):
        try:
            self.appir.driver.find_element_by_xpath('//h1[contains(text(), "Sorry, this room is full")]')
        except NoSuchElementException:
            return False
        return True

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
