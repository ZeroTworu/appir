import random
import time

from wipe.strategies.abc_strategy import AbstractWipeStrategy


class EnterExitStrategy(AbstractWipeStrategy):

    description = 'Стратегия заёба, рандом заходит-выходит (эффективно с fake-media)'

    def run_strategy(self):
        while self.is_working:
            wait_time = random.randint(1, 5)
            self.enter_room(room_url=self.room_url)
            self._logger.info('Entered at %s', self.room_url)
            if self.check_max_users:
                self._logger.info('Max users, now wait %d', wait_time)
                time.sleep(wait_time)
                self.exit_room()

    def _ban_callback(self):
        raise NotImplementedError
