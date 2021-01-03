from dataclasses import dataclass
from logging import Logger
from multiprocessing import Barrier
from typing import Callable, Optional


@dataclass
class WipeParams(object):
    room_url: str

    browser: str = 'firefox'
    headless: bool = True
    fake_media: bool = True
    others_params: Optional[dict] = None
    generator: str = 'zalgo'
    generator_length: int = 10
    max_users: int = 12
    barrier: Barrier = None
    use_barrier: bool = False
    logger: Logger = None


@dataclass
class PreparedStrategy(object):
    params: WipeParams
    strategy_class: Callable
