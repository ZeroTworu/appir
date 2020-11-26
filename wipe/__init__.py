__version__ = '0.2.3'  # noqa: WPS410

from wipe.wipe import FillRoomStrategy, YouTubeStrategy

STRATEGIES = {
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
}
