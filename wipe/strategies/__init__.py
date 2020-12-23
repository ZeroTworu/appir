from wipe.strategies.enter_exit_strategy import EnterExitStrategy
from wipe.strategies.fill_strategy import FillRoomStrategy
from wipe.strategies.flood_strategy import FloodStrategy
from wipe.strategies.youtube_strategy import YouTubeStrategy
from wipe.strategies.enter_refresh_strategy import EnterRefreshStrategy

STRATEGIES = {  # noqa: WPS407
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
    'ee': EnterExitStrategy,
    'flood': FloodStrategy,
    'er': EnterRefreshStrategy,
}
