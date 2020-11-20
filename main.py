import argparse
import logging
from argparse import RawTextHelpFormatter

from wipe.wipe import FillRoomStrategy, YouTubeStrategy

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

strategies = {
    'fill': FillRoomStrategy,
    'youtube': YouTubeStrategy,
}


def parse_args(args) -> dict:
    result = vars(args)
    result.pop('strategy')
    result.pop('url')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Appir Wipe v0.0.1.', formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'strategy',
        help="""
        `fill` - try to fill room by bots
        `youtube` - flood by youtube content
        """,
    )
    parser.add_argument(
        'url',
        help='room url',
    )
    parser.add_argument('--link', help='youtube link')
    parser.add_argument('--file', help='file with youtube links, one line - one link')

    args = parser.parse_args()

    strategy_class = strategies.get(args.strategy, None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', args.strategy)

    strategy = strategy_class(room_url=args.url, params=parse_args(args))
    strategy.run_strategy()
