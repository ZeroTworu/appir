import atexit
import logging
import random
import time
from functools import partial
from typing import Callable, Dict, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait
from wipe.browsers import Chrome, Firefox
from wipe.name_generator import NameGenerator
from wipe.params import WipeParams

drivers = {
    'firefox': Firefox,
    'chrome': Chrome,
}


class Appir(object):  # noqa: WPS214

    max_timeout = 5

    one_minute_timeout = 60

    min_timeout = 0.5

    min_poll_timeout = 0.1

    users: Dict[str, str] = {}

    def __init__(self, params: WipeParams):
        self._params = params
        self._browser = params.browser
        self._room_url: str = params.room_url
        self._barrier = params.barrier
        self._logger = params.logger
        self._opened_new_tab = False
        self._logger.setLevel(logging.DEBUG)

        generator = NameGenerator(params.generator, params.generator_length)
        self._generator = generator.get_generator()

        self._driver_class = drivers.get(params.browser.lower(), None)
        if self._driver_class is None:
            self._logger.error('Unknown browser %s', params.browser)
            return

        self.is_working = True
        self._init_driver()

    @property
    def is_whereby_open(self) -> bool:
        return 'Whereby' in self.driver.title

    @property
    def is_fool(self):
        try:
            self.driver.find_element_by_xpath('//h1[contains(text(), "Sorry, this room is full")]')
        except NoSuchElementException:
            return False
        return True

    @property
    def is_firefox(self):
        return self._browser == 'firefox'

    @property
    def is_chrome(self):
        return self._browser == 'chrome'

    @property
    def has_ban(self):
        try:
            self.driver.find_element_by_xpath('//h1[contains(text(), "Meeting ended")]')
        except NoSuchElementException:
            return False
        return True

    @property
    def no_access(self):
        try:
            self.driver.find_element_by_xpath('//strong[contains(text(), "You’ve not been granted access")]')
        except NoSuchElementException:
            return False
        return True

    @property
    def dont_login(self):
        return self.is_chrome and self.is_whereby_open and len(self.driver.window_handles) > 1

    def enter_room(self, room_url: str) -> bool:
        username = self._generator()
        self._room_url = room_url

        if self.is_whereby_open:
            self._opened_new_tab = True  # Для хрома помечаем что первый вход выполнен
            self.driver.open_new_tab()

        self._logger.debug('Waiting replay from whereby for url %s', self._room_url)
        self.driver.get(room_url)

        if self._barrier is not None:
            self._barrier.wait()

        entered = False
        # FF каждую новую вкладку, открывает незлогиненной в аппир
        # Chrome даже в режиме инкогнида открывает залогиненной под первым username
        if self.is_firefox:
            entered = self._ff_enter_room(username)
        elif self.is_chrome:
            entered = self._chrome_enter_room(username)

        if entered is not None and not entered:
            return self.enter_room(self._room_url)

        return self._append_user(username)

    def enter_login(self, username: str):
        try:
            enter_name = WebDriverWait(
                self.driver,
                self.one_minute_timeout,
                poll_frequency=self.min_poll_timeout,
            ).until(
                EC.presence_of_element_located((By.NAME, 'nickname')),
            )
        except TimeoutException:
            self._logger.warning('Cannot get "nickname" for %s', username)
            return False

        enter_name.send_keys(username)

        continue_btn = WebDriverWait(self.driver, self.max_timeout, poll_frequency=self.min_poll_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Continue")]')),
        )

        continue_btn.click()
        return True

    def join_room(self) -> bool:
        if self.no_access:
            self._logger.warning('No access to room %s close tab...', self._room_url)
            self.driver.close_tab()
            return False

        try:
            join_btn = WebDriverWait(
                self.driver,
                self.one_minute_timeout,
                poll_frequency=self.min_poll_timeout,
            ).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Join meeting")]')),
            )
        except TimeoutException:
            self._logger.warning('Cannot found "Join meeting"')
            return False

        join_btn.click()
        return True

    def check_locked(self, username):
        self._cancel_knock()
        try:
            knock_btn = WebDriverWait(self.driver, self.min_timeout, poll_frequency=self.min_poll_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Knock")]')),
            )
        except TimeoutException:
            return False

        knock_btn.click()

        wait_time = random.randint(5, 10)

        self._logger.info('Knock in %s, as %s, sleep %d...', self._room_url, username[:5], wait_time)

        try:
            WebDriverWait(self.driver, wait_time, poll_frequency=self.min_poll_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//figcaption[contains(text(), "Chat")]')),
            )
        except TimeoutException:
            self._logger.warning('Knock failed.')
            return self.check_locked(username)
        # Здесь мы могли быть впущены и пидорнуты
        self._logger.info('User %s successfully knocked to room %s.', username, self._room_url)
        return True

    def refresh_room(self):
        self._logger.info('Refreshing room...')
        self.driver.refresh()
        self.enter_login(self._generator())
        if self.is_firefox:
            if not self.join_room():
                self._logger.warning('Cannot refresh room, re-enter...')
                self.enter_room(self._room_url)

    def exit_room(self) -> None:
        current_window = self.driver.current_window_handle
        user = self.users.get(current_window, None)
        self.driver.close_tab()
        if user is None:
            self._logger.warning('Try get non-existent user %s, close tab only', current_window)
            return
        self.users.pop(current_window)
        self._logger.info('User %s left room', user)

    def try_stop_youtube(self) -> None:
        self._logger.info('Try stop youtube')
        try:
            self.driver.find_element_by_xpath('//div[contains(text(), "Stop sharing")]').click()
        except NoSuchElementException:
            self._logger.warning('No stop youtube btn')

    def check_and_handle_ban(self, callback: Callable = None):
        for window in self.users.copy().keys():
            time.sleep(0.5)
            self._check_ban(window, callback)

    def send_chat(self, msg: str) -> None:
        chat_btn = WebDriverWait(self.driver, self.max_timeout, poll_frequency=self.min_poll_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jstest-open-chat-button')),
        )

        chat_btn.click()

        message_area = WebDriverWait(self.driver, self.max_timeout, poll_frequency=self.min_poll_timeout).until(
            EC.presence_of_element_located((By.NAME, 'message')),
        )

        message_area.send_keys(msg)

        send_btn = self.driver.find_element_by_xpath('//div[contains(text(), "Send")]')
        send_btn.click()

    def start_youtube(self, link: str) -> bool:
        self.send_chat(link)

        start_youtube = WebDriverWait(self.driver, self.max_timeout, poll_frequency=self.min_poll_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "View together in room")]')),
        )

        start_youtube.click()

        try:
            WebDriverWait(self.driver, self.one_minute_timeout * 2, poll_frequency=self.min_poll_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'youtube-integration-contentframe')),
            )
        except TimeoutException:
            self._logger.warning('Cannot start YouTube - timeout wait')
            return False
        return True

    def _check_ban(self, window, callback: Callable = None) -> None:
        self.driver.switch_window(window)
        if self.has_ban:
            user = self.users.pop(window)
            self.driver.close_tab()
            self._logger.warning('User %s kicked', user)
            if callback is not None:
                callback()

    def _fix_cam_mic(self) -> None:
        try:
            WebDriverWait(self.driver, self.one_minute_timeout, poll_frequency=self.min_poll_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'figure')),
            )
        except TimeoutException:
            self._logger.warning('Cannot find settings btn')
            return

        settings = self.driver.find_elements_by_tag_name('figure')[:2]
        for btn in settings:
            btn.click()

    def _append_user(self, username):
        if not self.is_fool:
            self.users[self.driver.current_window_handle] = username
            self._logger.info('User %s login', username)
            return True
        self.driver.close()
        self._logger.warning('Room %s is fool, user %s does not need to be added', self._room_url, username)
        return False

    def _ff_enter_room(self, username) -> Optional[bool]:
        self.enter_login(username)

        if self.check_locked(username) is True:
            return self._cbar()
        return self.join_room()

    def _chrome_enter_room(self, username) -> Optional[bool]:
        if not self._opened_new_tab:
            return self._ff_enter_room(username)

        if self.check_locked(username) is True:
            return self._cbar()

    def _cancel_knock(self):
        try:
            cancel_btn = WebDriverWait(self.driver, self.min_timeout, poll_frequency=self.min_poll_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Cancel")]')),
            )
        except TimeoutException:
            return False

        cancel_btn.click()
        return True

    def _init_driver(self):
        self.driver = self._driver_class(headless=self._params.headless, fake_media=self._params.fake_media)
        atexit.register(self.driver.quit)

    def _cbar(self):
        return self._check_ban(self.driver.current_window_handle, partial(self.enter_room, self._room_url))
