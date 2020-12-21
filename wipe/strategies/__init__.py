from wipe.strategies.enter_exit_strategy import EnterExitStrategy
from wipe.strategies.fill_strategy import FillRoomStrategy
from wipe.strategies.youtube_strategy import YouTubeStrategy

STRATEGIES = {  # noqa: WPS407
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
    'ee': EnterExitStrategy,
}
