import abc
import uuid

from selenium.webdriver.remote.webdriver import WebDriver


class ABCWipeDriver(WebDriver):
    max_timeout = 5

    @abc.abstractmethod
    def close_tab(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def open_new_tab(self) -> None:
        raise NotImplementedError()

    def switch_tab_forward(self) -> None:
        self.switch_to.window(self.window_handles[-1])

    def switch_tab_back(self) -> None:
        back = len(self.window_handles) - 1
        if back > -1:
            self.switch_to.window(self.window_handles[back])
        else:
            self.switch_to.window(self.window_handles[0])

    def switch_window(self, window: str) -> bool:
        if window in self.window_handles:
            self.switch_to.window(window)
            return True
        return False

    def switch_to_last_window(self):
        window = self.window_handles[-1]
        return self.switch_window(window)

    def debug(self):
        name = f'{uuid.uuid4()}'
        self.save_screenshot(f'{name}.png')
        with open(f'{name}.html', 'w') as file:
            file.write(self.page_source)
        print(f'Saved {name}')  # noqa: WPS421
