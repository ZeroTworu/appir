import logging
from wipe.appir import Appir
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    appir = Appir(headless=False)
    appir.enter_room('https://whereby.com/alcojihad')
    appir.enter_room('https://whereby.com/alcojihad')
    appir.start_youtube('https://www.youtube.com/watch?v=NaIQlKKg1Y4')
    # while True:
    #     appir.check_ban()
