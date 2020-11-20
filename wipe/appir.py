import logging
import time
import uuid
from typing import Callable, Dict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import FirefoxProfile, Options
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait


class Appir(object):  # noqa: WPS214

    max_timeout = 60  # in seconds

    users: Dict[str, str] = {}

    def __init__(self, headless: bool = True):
        self.options = Options()
        self.options.headless = headless
        self.profile = FirefoxProfile()
        self.profile.set_preference('media.navigator.permission.disabled', True)
        self.profile.set_preference('permissions.default.microphone', 0)
        self.profile.set_preference('permissions.default.camera', 0)
        self.profile.set_preference('browser.tabs.remote.autostart', True)
        self.profile.set_preference('browser.tabs.remote.autostart.1', True)
        self.profile.set_preference('browser.tabs.remote.autostart.2', True)
        self.profile.set_preference('browser.privatebrowsing.autostart', True)
        self.profile.set_preference('media.volume_scale', '0.0')
        self.profile.update_preferences()

        self.driver = webdriver.Firefox(options=self.options, firefox_profile=self.profile)

    @property
    def _is_whereby_open(self) -> bool:
        return 'Whereby' in self.driver.title

    def enter_room(self, room_url: str) -> None:
        username = f'{uuid.uuid4()}'

        if self._is_whereby_open:
            self._open_new_tab()

        self.driver.get(room_url)

        enter_name = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.NAME, 'nickname')),
        )

        enter_name.send_keys(username)

        continue_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Continue")]')),
        )

        continue_btn.click()

        join_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Join meeting")]')),
        )
        self._fix_cam_mic()

        join_btn.click()
        self.users[self.driver.current_window_handle] = username
        logging.info('User %s login', username)

    def exit_room(self) -> None:
        current_window = self.driver.current_window_handle
        user = self.users[current_window]
        exit_btn = self.driver.find_element_by_class_name('jstest-leave-room-button')
        exit_btn.click()
        self._close_tab(current_window)
        logging.info('User %s left room', user)

    def try_stop_youtube(self) -> None:
        logging.info('Try stop youtube')
        try:
            self.driver.find_element_by_xpath('//div[contains(text(), "Stop sharing")]').click()
        except NoSuchElementException:
            logging.warning('No stop youtube btn')

    def check_ban(self, callback: Callable = None):
        for window, user in self.users.items():
            self.driver.switch_to.window(window)
            time.sleep(0.1)
            try:
                self._check_ban(window, user, callback)
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

    def _check_ban(self, window: str, user: str, callback: Callable):
        self.driver.find_element_by_xpath('//h1[contains(text(), "Meeting ended")]')
        self._close_tab(window)
        logging.warning('User %s kicked', user)
        if callback is not None:
            return callback(user)

    def _fix_cam_mic(self) -> None:
        settings = self.driver.find_elements_by_tag_name('figure')[:2]
        for btn in settings:
            btn.click()

    def _open_new_tab(self) -> None:
        current_windows_count = len(self.driver.window_handles)

        self.driver.execute('SET_CONTEXT', {'context': 'chrome'})
        self._send_keys_to_url_bar(Keys.CONTROL, 't')

        WebDriverWait(self.driver, self.max_timeout).until(
            EC.number_of_windows_to_be(current_windows_count + 1),
        )

        self.driver.execute('SET_CONTEXT', {'context': 'content'})
        self._switch_tab_forward()

    def _close_tab(self, window_handler) -> None:
        self.users.pop(window_handler)
        self.driver.execute('SET_CONTEXT', {'context': 'chrome'})
        self._send_keys_to_url_bar(Keys.CONTROL, 'w')
        self.driver.execute('SET_CONTEXT', {'context': 'content'})
        self._switch_tab_back()

    def _switch_tab_forward(self) -> None:
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _switch_tab_back(self) -> None:
        back = len(self.driver.window_handles) - 1
        if back > -1:
            self.driver.switch_to.window(self.driver.window_handles[back])
        else:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _send_keys_to_url_bar(self, *value) -> None:
        url_bar = self.driver.find_element_by_id('urlbar')
        url_bar.send_keys(value)
