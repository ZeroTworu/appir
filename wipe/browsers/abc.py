import abc


class ABCWipeDriver(object):
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
