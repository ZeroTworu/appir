import json
import logging
from typing import List

from flask import Flask, jsonify, render_template, request
from wipe import __version__
from wipe.logger import WipeLogRecordEncoder
from wipe.params import PreparedStrategy, WipeParams
from wipe.strategies import STRATEGIES
from wipe.threads import WipeThreadManager

app = Flask(__name__)

flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.ERROR)

manager: WipeThreadManager = None


def validate(form_data) -> List[str]:
    errors = []
    if form_data.get('room_url', '') == '':
        errors.append('Не указан адрес конфы')
    if form_data.get('wipe_type') == 'youtube' and form_data.get('youtube_url', '') == '':  # noqa: WPS221
        errors.append('Выбран вайп ютубом, но не указана ссылка на ролик')
    return errors


@app.route('/', methods=['GET'])
def index():
    params = {
        'version': __version__,
        'strategies': STRATEGIES,
    }
    return render_template('index.html', **params)


@app.route('/wipe/', methods=['POST'])
def wipe():  # noqa:  WPS210
    global manager  # noqa: WPS420
    form_data = request.json
    errors = validate(form_data)
    if bool(errors):
        return jsonify({'status': 'error', 'errors': errors})

    strategy_class = STRATEGIES.get(form_data['wipe_type'], None)

    if strategy_class is None:
        logging.error('Wrong strategy %s, write it by you self!', form_data['wipe_type'])
        return jsonify({'status': 'error'})

    wipe_params = WipeParams(
        room_url=form_data['room_url'],
        browser=form_data['browser'],
        fake_media=form_data.get('fake_media', 'off') == 'on',
        headless=True,
        others_params={'link': form_data.get('youtube_url', None)},
    )

    strategy = PreparedStrategy(params=wipe_params, strategy_class=strategy_class)
    manager = WipeThreadManager(strategy=strategy, threads_count=int(form_data.get('threads', 1)))  # noqa: WPS442
    manager.start()
    return jsonify({'status': 'started'})


@app.route('/status/', methods=['GET'])
def status():
    if manager is not None:
        logs = manager.get_logs()
        return json.dumps(logs, cls=WipeLogRecordEncoder)
    return json.dumps([])


@app.route('/stop/', methods=['GET'])
def stop():
    manager.stop()
    manager.logger.info('Wipe stopped.')
    manager.stop()
    manager.clear_logs()
    return jsonify({'status': 'stopped'})
