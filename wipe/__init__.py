__version__ = '0.2.5'  # noqa: WPS410

from wipe.wipe import FillRoomStrategy, YouTubeStrategy

STRATEGIES = {  # noqa: WPS407
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
}
