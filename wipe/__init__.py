__version__ = '0.2.2'

from wipe.wipe import FillRoomStrategy, YouTubeStrategy

STRATEGIES = {
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
}
