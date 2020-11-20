from selenium import webdriver
from selenium.webdriver.chrome.options import Options, DesiredCapabilities

from .abc import ABCWipeDriver


class Chrome(webdriver.Chrome, ABCWipeDriver):

    def __init__(self, headless: bool = True, *args, **kwargs):
        self.options = Options()

        desired_capabilities = DesiredCapabilities.CHROME.copy()
        desired_capabilities['applicationCacheEnabled'] = False

        if headless:
            self.options.add_argument('--headless')

        self.options.add_argument('--disable-gpu')

        self.options.add_argument('use-fake-device-for-media-stream')
        self.options.add_argument('use-fake-ui-for-media-stream')
        self.options.add_argument('--incognito')

        super().__init__(chrome_options=self.options, desired_capabilities=desired_capabilities, *args, **kwargs)

    def close_tab(self) -> None:
        self.close()
        self.switch_tab_back()

    def open_new_tab(self) -> None:
        self.execute_script('window.open('');')
        self.switch_tab_forward()
