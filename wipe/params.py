import logging
from multiprocessing import Barrier

import attr


@attr.s
class WipeParams(object):
    room_url: str = attr.ib()
    sid: str = attr.ib()

    browser: str = attr.ib(default='firefox')
    headless: bool = attr.ib(default=True)
    fake_media: bool = attr.ib(default=True)
    others_params: dict = attr.ib(default={})
    logger: logging = attr.ib(default=None)
    generator: str = attr.ib(default='zalgo')
    generator_length: int = attr.ib(default=10)
    max_users: int = attr.ib(default=12)
    barrier: Barrier = attr.ib(default=None)
    use_barrier: bool = attr.ib(default=False)


@attr.s
class PreparedStrategy(object):
    params: WipeParams = attr.ib()
    strategy_class = attr.ib()
