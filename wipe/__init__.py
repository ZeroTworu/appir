__version__ = '0.2.6'  # noqa: WPS410

from wipe.wipe import EnterExitStrategy, FillRoomStrategy, YouTubeStrategy

STRATEGIES = {  # noqa: WPS407
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
    'ee': EnterExitStrategy,
}
