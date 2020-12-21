import logging
from threading import Thread

from selenium.common.exceptions import InvalidSessionIdException
from wipe.strategies.abc_strategy import AbstractWipeStrategy


class WipeThread(Thread):

    def __init__(self, strategy: AbstractWipeStrategy, target, name):
        super().__init__(target=target, name=name)
        self.strategy = strategy

    def run(self):
        try:
            super().run()
        except InvalidSessionIdException as err:
            logging.error('Error after stop %s', err)

    def stop(self):
        self.strategy.stop_wipe()
