import atexit
import logging
import random
import time
import uuid
from functools import partial
from typing import Callable, Dict

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait
from wipe.browsers import Chrome, Firefox
from wipe.params import WipeParams

drivers = {
    'firefox': Firefox,
    'chrome': Chrome,
}


class Appir(object):  # noqa: WPS214

    max_timeout = 10

    youtube_timeout = 60

    min_timeout = 1.5

    users: Dict[str, str] = {}

    def __init__(self, params: WipeParams):
        driver_class = drivers.get(params.browser.lower(), None)
        if driver_class is None:
            logging.error('Unknown browser %s', params.browser)
            return

        self.is_working = True
        self._room_url: str = ''
        self.opened_new_tab = False

        self.driver = driver_class(headless=params.headless, fake_media=params.fake_media)
        self.knock = params.knock
        self._browser = params.browser
        self._sid = params.sid

        if params.logger is not None:
            self._logger = params.logger
        else:
            self._logger = logging.getLogger(__name__)

        self._logger.setLevel(logging.DEBUG)

        atexit.register(self.driver.quit)

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
    def dont_login(self):
        return self.is_chrome and self.is_whereby_open and len(self.driver.window_handles) > 1

    def enter_room(self, room_url: str) -> None:
        username = f'{uuid.uuid4()}'
        self._room_url = room_url

        if self.is_whereby_open:
            self.opened_new_tab = True  # Для хрома помечаем что первый вход выполнен
            self.driver.open_new_tab()

        self._logger.debug('Waiting replay from whereby for url %s', self._room_url)
        self.driver.get(room_url)

        # FF каждую новую вкладку, открывает незлогиненной в аппир
        # Chrome даже в режиме инкогнида открывает залогиненной под первым username
        if self.is_firefox:
            self._ff_enter_room(username)
        elif self.is_chrome:
            self._chrome_enter_room(username)

        self._append_user(username)

    def enter_login(self, username: str):
        enter_name = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.NAME, 'nickname')),
        )

        enter_name.send_keys(username)

        continue_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Continue")]')),
        )

        continue_btn.click()

    def join_room(self):
        join_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Join meeting")]')),
        )

        join_btn.click()

    def check_locked(self, username):
        self._cancel_knock()
        try:
            knock_btn = WebDriverWait(self.driver, self.min_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Knock")]')),
            )
        except TimeoutException:
            return False

        knock_btn.click()

        wait_time = self.max_timeout * random.randint(1, 10)

        self._logger.info('Knock in %s, sleep %d...', self._room_url, wait_time)

        try:
            WebDriverWait(self.driver, wait_time, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.XPATH, '//figcaption[contains(text(), "Chat")]')),
            )
        except TimeoutException:
            self._logger.warning('Knock failed.')
            return self.check_locked(username)
        # Здесь мы могли быть впущены и пидорнуты
        self._logger.info('User %s successfully knocked to room %s.', username, self._room_url)
        return True

    def exit_room(self) -> None:
        current_window = self.driver.current_window_handle
        user = self.users[current_window]

        try:
            exit_btn = self.driver.find_element_by_class_name('jstest-leave-room-button')
        except NoSuchElementException:
            self._logger.warning('Cannot found exit btn %s', user)
            return

        exit_btn.click()
        self.driver.close_tab()
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
        chat_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jstest-open-chat-button')),
        )

        chat_btn.click()

        message_area = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.NAME, 'message')),
        )

        message_area.send_keys(msg)

        send_btn = self.driver.find_element_by_xpath('//div[contains(text(), "Send")]')
        send_btn.click()

    def start_youtube(self, link: str) -> None:
        self.send_chat(link)

        start_youtube = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "View together in room")]')),
        )

        start_youtube.click()

        try:
            WebDriverWait(self.driver, self.youtube_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Stop sharing")]')),
            )
        except TimeoutException:
            self._logger.warning('Cannot start YouTube - timeout wait')

    def _check_ban(self, window, callback: Callable = None):
        self.driver.switch_window(window)
        if self.has_ban:
            user = self.users.pop(window)
            self.driver.close_tab()
            self._logger.warning('User %s kicked', user)
            if callback is not None:
                callback()

    def _check_fool(self, window):
        self.driver.switch_window(window)
        self.driver.close_tab()
        self._logger.warning('Closed tab %s because is fool', window)

    def _fix_cam_mic(self) -> None:
        try:
            WebDriverWait(self.driver, self.youtube_timeout).until(
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
            return
        self._logger.warning('Room %s is fool, user %s does not need to be added', self._room_url, username)

    def _ff_enter_room(self, username):
        self.enter_login(username)

        if self.knock and self.check_locked(username) is True:
            self._check_ban(self.driver.current_window_handle, partial(self.enter_room, self._room_url))
        else:
            self.join_room()

    def _chrome_enter_room(self, username):
        if not self.opened_new_tab:
            return self._ff_enter_room(username)

        if self.knock and self.check_locked(username) is True:
            self._check_ban(self.driver.current_window_handle, partial(self.enter_room, self._room_url))

    def _cancel_knock(self):
        try:
            cancel_btn = WebDriverWait(self.driver, self.min_timeout, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Cancel")]')),
            )
        except TimeoutException:
            return False

        cancel_btn.click()
        return True
