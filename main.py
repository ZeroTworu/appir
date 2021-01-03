import argparse
import logging
from argparse import RawTextHelpFormatter

from wipe import __version__
from wipe.params import PreparedStrategy, WipeParams
from wipe.strategies import STRATEGIES
from wipe.threads import WipeThreadManager


def handle_main(args):
    strategy_class = STRATEGIES.get(args.strategy, None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', args.strategy)
        return

    wipe_params = WipeParams(
        room_url=args.url,
        browser=args.browser,
        headless=args.headless == '1',
        fake_media=args.fake_media == '1',
        generator=args.name_generator,
        generator_length=args.name_length,
        others_params={'link': args.link, 'file': args.file, 'phrase': args.phrase},
        max_users=args.max_users,
        use_barrier=args.use_barrier == '1',
    )

    strategy = PreparedStrategy(params=wipe_params, strategy_class=strategy_class)
    manager = WipeThreadManager(strategy=strategy, threads_count=args.threads)
    manager.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Whereby Wipe v{__version__}', formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'strategy',
        help="""
        `fill` - try to fill room by bots
        `youtube` - flood by youtube content
        `ee` - Enter&Exit random into room on few seconds, effectively with `--fake-media=1`
        `flood` - just flood in chat
        """,
    )
    parser.add_argument(
        'url',
        help='room url',
    )
    parser.add_argument('--link', help='youtube link')
    parser.add_argument('--file', help='file with youtube links or flood phrases, one line - one link')

    parser.add_argument('--browser', help='browser for user, chrome or firefox default - firefox', default='firefox')
    parser.add_argument('--headless', help='if 1 run without GUI', default='1')
    parser.add_argument('--fake-media', help='if 1 browser use fake video&audio streams', default='1')
    parser.add_argument(
        '--name-generator',
        help='Generator to generate names (uuid, russian, english, mixed, zalgo)',
        default='zalgo',
    )

    parser.add_argument('--name-length', type=int, help='length of generated name', default=10)
    parser.add_argument('--max-users', type=int, help='Max users in room, 0 for infinity, default 12', default=12)
    parser.add_argument('--phrase', type=str, help='Flood phrase', default='ziga-zaga!')
    parser.add_argument('--threads', type=int, help='count of wipe threads', default=1)
    parser.add_argument('--use-barrier', help='Use barrier for wipe threads', default='0')

    args = parser.parse_args()

    handle_main(args)
