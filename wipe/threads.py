import logging
from threading import Barrier, Thread
from typing import List, Optional

from selenium.common.exceptions import InvalidSessionIdException
from wipe.params import PreparedStrategy
from wipe.strategies.abc_strategy import AbstractWipeStrategy


class WipeThread(Thread):

    def __init__(self, strategy: PreparedStrategy, name: str, barrier: Barrier = None):
        self.strategy: Optional[AbstractWipeStrategy] = None
        self.prepared_strategy = strategy
        self.prepared_strategy.params.barrier = barrier
        logging.info('Init "thread %s"', name)
        super().__init__(name=name)

    def run(self):
        self.strategy = self.prepared_strategy.strategy_class(self.prepared_strategy.params)
        try:
            self.strategy.start()
        except InvalidSessionIdException as err:
            logging.error('Error after stop %s', err)

    def stop(self):
        self.strategy.stop()


class WipeThreadManager(object):
    threads: List[WipeThread] = []

    def __init__(self, strategy: PreparedStrategy, threads_count: int = 1):
        self.prepared_strategy = strategy
        self.threads_count = threads_count
        if strategy.params.use_barrier:
            self.barrier = Barrier(threads_count)
        else:
            self.barrier = None

    def start(self):
        for num in range(self.threads_count):
            thread = WipeThread(strategy=self.prepared_strategy, name=f'Wipe Thread №{num}', barrier=self.barrier)
            self.threads.append(thread)
            thread.start()

        if self.barrier is not None:
            self.barrier.wait()

    def stop(self):
        for thread in self.threads:
            thread.stop()

    def stop_thread(self, num: int):
        thread = self.threads.pop(num)
        thread.stop()
