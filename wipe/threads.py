import logging
from threading import Thread
from typing import Dict

from selenium.common.exceptions import InvalidSessionIdException
from wipe.params import PreparedStrategy
from wipe.strategies.abc_strategy import AbstractWipeStrategy


class WipeThread(Thread):

    def __init__(self, strategy: PreparedStrategy, name: str):
        self.strategy: AbstractWipeStrategy = None
        self.prepared_strategy = strategy
        super().__init__(name=name)

    def run(self):
        try:
            self.strategy = self.prepared_strategy.strategy_class(self.prepared_strategy.params)
            self.strategy.start()
        except InvalidSessionIdException as err:
            logging.error('Error after stop %s', err)

    def stop(self):
        self.strategy.stop()


class WipeThreadManager(object):

    threads: Dict[int, WipeThread] = {}

    def __init__(self, strategy: PreparedStrategy, threads_count: int = 1):
        self.prepared_strategy = strategy
        self.threads_count = threads_count

    def start(self):
        for num in range(self.threads_count):
            thread = WipeThread(strategy=self.prepared_strategy, name=f'Wipe Thread №{num}')
            self.threads[num] = thread
            thread.start()

    def stop_all(self):
        for thread in self.threads.items():
            thread.stop()

    def stop_thread(self, num: int):
        thread = self.threads.pop(num)
        thread.stop()
