import time
from threading import Lock, Thread

from wipe.strategies.abc_strategy import AbstractWipeStrategy


class FillRoomStrategy(AbstractWipeStrategy):

    max_timeout = 1.5

    description = 'Попытка заполнить комнату до отказа'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.mutex = Lock()
        self.need_check = False
        self.check_thread = None
        self.init_control()

    def re_run(self):
        self.need_check = False
        self._is_waiting_ban = False
        self.mutex.release()
        time.sleep(2)
        self.check_thread.join()
        super().re_run()
        self.init_control()

    def init_control(self):
        self.need_check = True
        self.check_thread = Thread(target=self.check_thread, name='Control ban thread')
        self.check_thread.start()

    def run_strategy(self):
        while self.is_working:
            self.mutex.acquire()
            self.need_check = self.enter_room(room_url=self.room_url)
            self.mutex.release()
            time.sleep(self.max_timeout)
            if not self.need_check or self.check_max_users:
                self._is_waiting_ban = True
                self._logger.warning('Room %s fool, waiting for bans...', self.room_url)
                self.wait_ban()

    def check_thread(self):
        while self.is_need_thread:
            self.mutex.acquire()
            self.check_and_handle_ban()
            self.mutex.release()
            time.sleep(0.5)

    @property
    def is_need_thread(self):
        return not self._is_waiting_ban and self.need_check and self.is_working

    def _ban_callback(self, *args, **kwargs):
        self.is_waiting_ban = False
        self.need_check = True
