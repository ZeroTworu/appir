import argparse
import logging
import uuid
from argparse import RawTextHelpFormatter

from wipe import STRATEGIES, __version__
from wipe.wipe import WipeParams

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)


def handle_main(args):
    strategy_class = STRATEGIES.get(args.strategy, None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', args.strategy)
        return

    wipe_params = WipeParams(
        room_url=args.url,
        browser=args.browser,
        headless=args.headless == '1',
        knock=args.knock == '1',
        fake_media=args.fake_media == '1',
        generator=args.name_generator,
        generator_length=args.name_length,
        others_params={'link': args.link, 'file': args.file},
        max_users=args.max_users,
        sid=f'{uuid.uuid4()}',
    )

    strategy = strategy_class(wipe_params)
    strategy.run_strategy()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Whereby Wipe v{__version__}', formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'strategy',
        help="""
        `fill` - try to fill room by bots
        `youtube` - flood by youtube content
        `ee` - Enter&Exit random into room on few seconds, effectively with `--fake-media=1`
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
    parser.add_argument('--headless', help='if 1 run without GUI', default='1')
    parser.add_argument('--fake-media', help='if 1 browser use fake video&audio streams', default='1')
    parser.add_argument(
        '--name-generator',
        help='Generator to generate names (uuid, russian, english, mixed, zalgo)',
        default='zalgo',
    )

    parser.add_argument('--name-length', type=int, help='length of generated name', default=10)
    parser.add_argument('--max-users', type=int, help='Max users in room, 0 for infinity, default 12', default=12)

    args = parser.parse_args()

    handle_main(args)
