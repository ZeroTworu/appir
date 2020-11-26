import uuid
import logging
import threading
from typing import List

from flask import Flask, jsonify, render_template, request
from web.web_handler import LOGS, WebHandler
from wipe import STRATEGIES, __version__
from wipe.wipe import WipeParams

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(WebHandler())


def validate(form_data: dict) -> List[str]:
    errors = []
    if form_data.get('room_url', '') == '':
        errors.append('Не указан адрес конфы')
    if form_data.get('wipe_type') == 'youtube' and form_data.get('youtube_url', '') == '':  # noqa: WPS221
        errors.append('Выбран вайп ютубом, но не указана ссылка на ролик')
    return errors


def run_wipe(form_data):
    strategy_class = STRATEGIES.get(form_data['wipe_type'], None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', form_data['wipe_type'])
        return

    wipe_params = WipeParams(
        room_url=form_data['room_url'],
        browser=form_data['browser'],
        knock=form_data.get('knock', 'off') == 'on',
        fake_media=form_data.get('fake_media', 'off') == 'on',
        headless=True,
        others_params={'link': form_data.get('youtube_url', None)},
        logger=logger,
    )

    strategy = strategy_class(wipe_params)
    thread = threading.Thread(target=strategy.run_strategy)
    thread.start()


@app.route('/')
def hello_world():
    params = {
        'version': __version__,
        'strategies': STRATEGIES,
        'user_id': f'{uuid.uuid4()}',
    }
    return render_template('index.html', **params)


@app.route('/wipe', methods=['POST'])
def wipe():
    form_data = request.json
    errors = validate(form_data)
    if bool(errors):
        return jsonify({'status': 'error', 'errors': errors})
    run_wipe(form_data)
    return jsonify({'status': 'started'})


@app.route('/status')
def status():
    if bool(LOGS):
        return jsonify(
            log=LOGS.pop(),
        )
    return jsonify({})
