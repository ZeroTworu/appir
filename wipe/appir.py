import atexit
import logging
import random
import time
import uuid
from typing import Callable

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait
from wipe.browsers import Chrome, Firefox

drivers = {
    'firefox': Firefox,
    'chrome': Chrome,
}


class Appir(object):  # noqa: WPS214

    max_timeout = 5

    youtube_timeout = 60

    min_timeout = 1.5

    users = {}

    def __init__(self, headless: bool = True, browser: str = 'firefox', knock: bool = True):
        driver_class = drivers.get(browser.lower(), None)
        if driver_class is None:
            logging.error('Unknown browser %s', browser)
            return
        self.browser = browser
        self.opened_new_tab = False
        self.driver = driver_class(headless=headless)
        self.knock = knock
        self.room_url: str = ''

        atexit.register(self.driver.quit)

    @property
    def is_whereby_open(self) -> bool:
        return 'Whereby' in self.driver.title

    @property
    def is_fool(self):
        try:
            WebDriverWait(self.driver, self.min_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Sorry, this room is full")]')),
            )
        except TimeoutException:
            return False
        return True

    @property
    def is_firefox(self):
        return self.browser == 'firefox'

    @property
    def is_chrome(self):
        return self.browser == 'chrome'

    def enter_room(self, room_url: str) -> None:
        username = f'{uuid.uuid4()}'
        self.room_url = room_url

        if self.is_whereby_open:
            self.opened_new_tab = True
            self.driver.open_new_tab()

        self.driver.get(room_url)

        if (self.is_chrome and not self.opened_new_tab) or self.is_firefox:
            enter_name = WebDriverWait(self.driver, self.max_timeout).until(
                EC.presence_of_element_located((By.NAME, 'nickname')),
            )

            enter_name.send_keys(username)

            continue_btn = WebDriverWait(self.driver, self.max_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Continue")]')),
            )

            continue_btn.click()

            if self.knock:
                self.check_locked()

            join_btn = WebDriverWait(self.driver, self.max_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Join meeting")]')),
            )
            self._fix_cam_mic()

            join_btn.click()

        self.users[self.driver.current_window_handle] = username

        logging.info('User %s login', username)

    def check_locked(self):
        try:
            knock_btn = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Knock")]')),
            )
        except TimeoutException:
            return False

        self._fix_cam_mic()

        knock_btn.click()
        wait_time = random.randint(5, 20)
        logging.info('Knock in %s, sleep %d...', self.room_url, wait_time)
        time.sleep(wait_time)

        try:
            cancel_btn = WebDriverWait(self.driver, self.max_timeout).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Cancel")]')),
            )
        except TimeoutException:
            return False
        cancel_btn.click()
        return self.check_locked()

    def exit_room(self) -> None:
        current_window = self.driver.current_window_handle
        user = self.users[current_window]
        exit_btn = self.driver.find_element_by_class_name('jstest-leave-room-button')
        exit_btn.click()
        self.driver.close_tab()
        self.users.pop(current_window)
        logging.info('User %s left room', user)

    def try_stop_youtube(self) -> None:
        logging.info('Try stop youtube')
        try:
            self.driver.find_element_by_xpath('//div[contains(text(), "Stop sharing")]').click()
        except NoSuchElementException:
            logging.warning('No stop youtube btn')

    def check_ban(self, callback: Callable = None):
        for window in self.users.keys():
            self.driver.switch_to.window(window)
            time.sleep(0.1)
            try:
                return self._check_ban(window, callback)
            except NoSuchElementException:
                pass  # noqa: WPS420

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
            logging.warning('Cannot start YouTube - timeout wait')

    def _check_ban(self, window: str, callback: Callable):
        self.driver.find_element_by_xpath('//h1[contains(text(), "Meeting ended")]')
        user = self.users.pop(window)
        self.driver.close_tab()
        logging.warning('User %s kicked', user)
        if callback is not None:
            return callback(user), True

    def _fix_cam_mic(self) -> None:
        settings = self.driver.find_elements_by_tag_name('figure')[:2]
        for btn in settings:
            btn.click()
