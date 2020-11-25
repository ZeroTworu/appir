import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait
from wipe.browsers.abc import ABCWipeDriver


class Chrome(webdriver.Chrome, ABCWipeDriver):

    def __init__(self, headless: bool = True, *args, **kwargs):
        self.options = Options()

        if headless:
            self.options.add_argument('--headless')

        self.options.add_argument('--disable-gpu')

        self.options.add_argument('use-fake-device-for-media-stream')
        self.options.add_argument('use-fake-ui-for-media-stream')

        super().__init__(chrome_options=self.options, *args, **kwargs)

    def close_tab(self) -> None:
        if len(self.window_handles) > 1:
            self.close()
            self.switch_tab_back()

    def open_new_tab(self) -> None:
        self.execute_script('window.open();')
        self.switch_tab_forward()

    def delete_cache(self):
        self.get('chrome://settings/clearBrowserData')

        WebDriverWait(self, self.max_timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'settings-ui')),
        )
        time.sleep(2)
        actions = ActionChains(self)
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)  # send right combination
        actions.perform()
        time.sleep(2)
        actions = ActionChains(self)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER)  # confirm
        actions.perform()
