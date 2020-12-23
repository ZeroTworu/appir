import random
import threading
import time

from wipe.strategies.abc_strategy import AbstractWipeStrategy


class EnterRefreshStrategy(AbstractWipeStrategy):

    description = 'Стратегия заёба №2 (эффективно с fake-media)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.name = threading.current_thread().getName()
        self.enter()

    def enter(self):
        self.enter_room(room_url=self._room_url)
        self._logger.info('Entered at %s', self._room_url)

    def run_strategy(self):
        while self.is_working:
            wait_time = random.randint(4, 8)
            self._logger.info(f'{self.name} now wait %d', wait_time)
            time.sleep(wait_time)
            self.refresh_room()

    def _ban_callback(self):
        self.enter()
