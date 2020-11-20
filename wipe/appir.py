import logging
import uuid
import time
from typing import Dict

from selenium import webdriver
from selenium.webdriver.firefox.options import Options, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class Appir(object):

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
        self.profile.update_preferences()

        self.driver = webdriver.Firefox(options=self.options, firefox_profile=self.profile)

    def enter_room(self, room_link: str) -> None:
        username = f'{uuid.uuid4()}'
        is_open_room = self._is_room_open()
        if is_open_room:
            self._open_new_tab()
            self._switch_tab_forward()

        self.driver.get(room_link)

        enter_name = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.NAME, 'nickname'))
        )

        enter_name.send_keys(username)

        self.driver.find_element_by_xpath('//div[contains(text(), "Continue")]').click()

        join_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Join meeting")]'))
        )
        self._fix_cam_mic()

        join_btn.click()
        self.users[username] = self.driver.current_window_handle
        logging.info('User %s login', username)

    def _fix_cam_mic(self) -> None:
        settings = self.driver.find_elements_by_tag_name('figure')
        for btn in settings[0:2]:
            btn.click()

    def _is_room_open(self) -> bool:
        try:
            self.driver.find_element_by_class_name('jstest-leave-room-button')
        except NoSuchElementException:
            return False
        return True

    def _open_new_tab(self):
        self.driver.execute('SET_CONTEXT', {'context': 'chrome'})
        url_bar = self.driver.find_element_by_id('urlbar')
        url_bar.send_keys(Keys.CONTROL, 't')
        self.driver.execute('SET_CONTEXT', {'context': 'content'})

    def _close_tab(self):
        self.driver.execute('SET_CONTEXT', {'context': 'chrome'})
        url_bar = self.driver.find_element_by_id('urlbar')
        url_bar.send_keys(Keys.CONTROL, 'w')
        self.driver.execute('SET_CONTEXT', {'context': 'content'})

    def _switch_tab_forward(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _switch_tab_back(self):
        back = len(self.driver.window_handles) - 1
        if back > -1:
            self.driver.switch_to.window(self.driver.window_handles[back])

    def check_ban(self):
        for user, window in self.users.items():
            self.driver.switch_to.window(window)
            time.sleep(2)
            try:
                self.driver.find_element_by_xpath('//h1[contains(text(), "Meeting ended")]')
                self._close_tab()
                del self.users[user]
                logging.warning('User %s kicked', user)
                return self.check_ban()
            except NoSuchElementException:
                logging.info('User %s steel in room', user)

    def send_chat(self, msg: str):
        chat_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jstest-open-chat-button'))
        )

        chat_btn.click()

        message_area = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.NAME, 'message'))
        )

        message_area.send_keys(msg)

        send_btn = self.driver.find_element_by_xpath('//div[contains(text(), "Send")]')
        send_btn.click()

    def start_youtube(self, link: str):
        self.send_chat(link)

        start_youtube = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "View together in room")]'))
        )

        start_youtube.click()
