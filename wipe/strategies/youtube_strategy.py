import random
import time

from wipe.strategies.abc_strategy import AbstractWipeStrategy


class YouTubeStrategy(AbstractWipeStrategy):
    description = 'Постоянно заходит рандом и включает ютуб'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_link = None
        self.links = None

    def run_strategy(self):
        self.youtube_link = self.params.get('link')
        youtube_file = self.params.get('file', None)
        if youtube_file is not None:
            self._parse_youtube_file(youtube_file)

        while self.is_working:
            wait_time = random.randint(20, 60)
            self.enter_room(room_url=self.room_url)
            if bool(self.users):
                if self._start_youtube():

                    self._logger.warning('Youtube %s started, wait %d seconds...', self.youtube_link, wait_time)
                    time.sleep(wait_time)

                    self.try_stop_youtube()
                    self.exit_room()
                else:
                    self._logger.warning('Possible Youtube disabled in %s or whereby lag', self.room_url)
            else:
                self._logger.info('Possible room is fool or no access, waiting 1 min')
                time.sleep(self.one_minute_timeout)

    def _ban_callback(self, *args, **kwargs):
        raise NotImplementedError

    def _start_youtube(self):
        if self.links is not None:
            self.youtube_link = random.choice(self.links)
            return self.start_youtube(self.youtube_link)
        return self.start_youtube(self.youtube_link)

    def _parse_youtube_file(self, file):
        with open(file, 'r') as read:
            self.links = read.readlines()
