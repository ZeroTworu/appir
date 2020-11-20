import atexit
import logging
import time
import uuid
from typing import Callable, Dict, List
import random

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait

from wipe.browsers import Chrome, Firefox

drivers = {
    'firefox': Firefox,
    'chrome': Chrome,
}


class Appir(object):  # noqa: WPS214

    max_timeout = 60  # in seconds

    users: List[dict] = []

    def __init__(self, headless: bool = True, browser: str = 'firefox'):
        driver_class = drivers.get(browser.lower(), None)
        if driver_class is None:
            logging.error('Unknown browser %s', browser)
            return
        self.browser = browser
        self.opened_new_tab = False
        self.driver = driver_class(headless=headless)

    @property
    def _is_whereby_open(self) -> bool:
        return 'Whereby' in self.driver.title

    def enter_room(self, room_url: str) -> None:
        username = f'{uuid.uuid4()}'
        self.room_url = room_url

        if self._is_whereby_open:
            self.opened_new_tab = True
            self.driver.open_new_tab()

        self.driver.get(room_url)

        if self.browser == 'chrome' and not self.opened_new_tab:
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

        self.users.append({
            'username': username,
            'window': self.driver.current_window_handle
        })

        logging.info('User %s login', username)

    def check_locked(self):
        knock_btn = None
        try:
            knock_btn = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Knock")]')),
            )
        except TimeoutException:
            return False

        self.global_lock = True
        self._fix_cam_mic()

        if knock_btn is not None:
            knock_btn.click()
        wait_time = random.randint(5, 20)
        logging.info('Knock in %s, sleep %d...',self.room_url, wait_time)
        time.sleep(wait_time)

        cancel_btn = WebDriverWait(self.driver, self.max_timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Cancel")]')),
        )
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
        for window_user in self.users:
            self.driver.switch_to.window(window_user['window'])
            logging.info('Switch to %s', window_user['window'])
            time.sleep(0.1)
            try:
                self.driver.find_element_by_xpath('//h1[contains(text(), "Meeting ended")]')
                self.driver.close_tab()
                window_index = self.users.index(window_user)
                self.users.pop(window_index)
                logging.warning('User %s kicked', window_user['username'])
                if callback is not None:
                    return callback(window_user['username'])
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
