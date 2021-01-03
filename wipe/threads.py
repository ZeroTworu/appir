import logging
from threading import Barrier, Thread
from typing import List, Optional

from selenium.common.exceptions import InvalidSessionIdException
from wipe.logger import WipeLogHandler
from wipe.params import PreparedStrategy
from wipe.strategies.abc_strategy import AbstractWipeStrategy

logging.basicConfig(format='%(threadName)s %(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)


class WipeThread(Thread):

    def __init__(self, strategy: PreparedStrategy, name: str):
        self.strategy: Optional[AbstractWipeStrategy] = None
        self.prepared_strategy = strategy
        self._logger = self.prepared_strategy.params.logger
        self._logger.info('Init "thread %s"', name)
        super().__init__(name=name)

    def run(self):
        self.strategy = self.prepared_strategy.strategy_class(self.prepared_strategy.params)
        try:
            self.strategy.start()
        except InvalidSessionIdException as err:
            self._logger.error('Error after stop %s', err)

    def stop(self):
        self.strategy.stop()


class WipeThreadManager(object):
    logger = logging.getLogger(__name__)

    _threads: List[WipeThread] = []

    def __init__(self, strategy: PreparedStrategy, threads_count: int = 1):
        self.prepared_strategy = strategy
        self._handler = WipeLogHandler()
        self.logger.addHandler(self._handler)

        self.prepared_strategy.params.logger = self.logger
        self.threads_count = threads_count

        if strategy.params.use_barrier:
            self.barrier = Barrier(threads_count)
        else:
            self.barrier = None
        self.prepared_strategy.params.barrier = self.barrier

    def start(self):
        for num in range(self.threads_count):
            thread = WipeThread(strategy=self.prepared_strategy, name=f'Wipe Thread №{num}')
            self._threads.append(thread)
            thread.start()

        if self.barrier is not None:
            self.barrier.wait()

    def stop(self):
        for thread in self._threads:
            thread.stop()
        self.logger.info('Stopped all threads')

    def stop_thread(self, num: int):
        thread = self._threads.pop(num)
        thread.stop()
        self.logger.info('Thread %s stopped', thread.getName())

    def get_logs(self):
        return self._handler.get_logs()

    def clear_logs(self):
        self._handler.clear_logs()
