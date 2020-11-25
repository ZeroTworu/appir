from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import FirefoxProfile, Options
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait
from wipe.browsers.abc import ABCWipeDriver


class Firefox(webdriver.Firefox, ABCWipeDriver):

    def __init__(self, headless=True, fake_media: bool = True, *args, **kwargs):
        self.fake_media = fake_media
        self.options = Options()
        self.options.headless = headless
        self.profile = FirefoxProfile()
        self._set_options()
        self.profile.update_preferences()

        super().__init__(options=self.options, firefox_profile=self.profile, *args, **kwargs)

    def send_keys_to_url_bar(self, *value) -> None:
        url_bar = self.find_element_by_id('urlbar')
        url_bar.send_keys(value)

    def open_new_tab(self) -> None:
        current_windows_count = len(self.window_handles)

        self.execute('SET_CONTEXT', {'context': 'chrome'})
        self.send_keys_to_url_bar(Keys.CONTROL, 't')

        WebDriverWait(self, self.max_timeout).until(
            EC.number_of_windows_to_be(current_windows_count + 1),
        )

        self.execute('SET_CONTEXT', {'context': 'content'})
        self.switch_tab_forward()

    def close_tab(self) -> None:
        if len(self.window_handles) > 1:
            self.execute('SET_CONTEXT', {'context': 'chrome'})
            self.send_keys_to_url_bar(Keys.CONTROL, 'w')
            self.execute('SET_CONTEXT', {'context': 'content'})
            self.switch_tab_back()

    def _set_options(self):
        self.profile.set_preference('media.navigator.permission.disabled', True)
        self.profile.set_preference('permissions.default.microphone', 0)
        self.profile.set_preference('permissions.default.camera', 0)
        self.profile.set_preference('browser.tabs.remote.autostart', True)
        self.profile.set_preference('browser.privatebrowsing.autostart', True)
        self.profile.set_preference('media.volume_scale', '0.0')
        if self.fake_media:
            self.options.set_preference('media.navigator.streams.fake', True)
