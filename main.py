import logging

from wipe.wipe import FillRoomStrategy

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    strg = FillRoomStrategy('https://whereby.com/alcojihad', headless=False)
    strg.run_strategy()
