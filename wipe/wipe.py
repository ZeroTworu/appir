import abc
import logging

from selenium.common.exceptions import NoSuchElementException
from wipe.appir import Appir


class WipeStrategy(object):

    def __init__(self, room_url: str, params: dict = None, headless: bool = True):
        self.appir = Appir(headless=headless)
        self.params = params
        self.room_url = room_url

    @abc.abstractmethod
    def run_strategy(self):
        raise NotImplementedError


class FillRoomStrategy(WipeStrategy):

    is_waiting_ban = False

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

    def wait_ban(self):
        while self.is_waiting_ban:
            self.appir.check_ban(self._ban_callback)

    def _ban_callback(self, *args, **kwargs):
        self.is_waiting_ban = False
