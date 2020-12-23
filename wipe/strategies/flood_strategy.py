import random
import time

from wipe.strategies.abc_strategy import AbstractWipeStrategy


class FloodStrategy(AbstractWipeStrategy):

    description = 'Флуд - он и в африке флуд'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file = self.strategy_params.get('file', None)
        phrase = self.strategy_params.get('phrase', None)

        if file is None and phrase is None:
            raise ValueError('file and phrase is None')

        if file is not None:
            with open(file, 'r') as readed_file:
                self.phrases = readed_file.readlines()
        self.phrase = phrase

    def run_strategy(self):
        self.enter_room(room_url=self._room_url)
        self._logger.info('Entered at %s', self._room_url)
        while self.is_working:
            if self.phrases is not None:
                self.phrase = random.choice(self.phrases)
            self._logger.info(f'Send phrase "{self.phrase}"')
            self.send_chat(self.phrase)
            time.sleep(random.randint(3, 6))

    def _ban_callback(self):
        raise NotImplementedError
