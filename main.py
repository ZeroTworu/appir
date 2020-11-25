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
    result = vars(args)  # noqa: WPS421
    for param in ('strategy', 'url', 'knock', 'headless', 'browser'):
        result.pop(param)
    return result


def handle_main(args):
    strategy_class = strategies.get(args.strategy, None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', args.strategy)
        return

    strategy = strategy_class(
        room_url=args.url,
        browser=args.browser,
        headless=args.headless == '1',
        knock=args.knock == '1',
    )

    strategy.set_params(params=parse_args(args))
    strategy.run_strategy()


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

    parser.add_argument('--browser', help='browser for user, chrome or firefox default - firefox', default='firefox')
    parser.add_argument('--knock', help='knock to conference if locked', default='1')
    parser.add_argument('--headless', help='if 0 run without GUI', default='1')

    args = parser.parse_args()

    handle_main(args)
