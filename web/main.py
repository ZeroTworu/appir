import json
import logging
import uuid
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from web.web_handler import WebHandler, WipeLogRecordEncoder
from wipe import __version__
from wipe.params import WipeParams
from wipe.strategies import STRATEGIES
from wipe.threads import WipeThread

app = Flask(__name__)

logging.basicConfig(format='%(threadName)s-%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.addHandler(WebHandler())

flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.ERROR)


threads: Dict[str, WipeThread] = {}


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
        sid=form_data['sid'],
        browser=form_data['browser'],
        fake_media=form_data.get('fake_media', 'off') == 'on',
        headless=True,
        others_params={'link': form_data.get('youtube_url', None)},
        logger=logger,
    )

    strategy = strategy_class(wipe_params)
    thread = WipeThread(strategy=strategy, name=form_data['sid'])
    threads[form_data['sid']] = thread
    thread.start()


@app.route('/')
def hello_world():
    params = {
        'version': __version__,
        'strategies': STRATEGIES,
        'sid': f'{uuid.uuid4()}',
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
    user_id = request.args.get('sid')
    logs = WebHandler.get_logs(user_id)
    return json.dumps(logs, cls=WipeLogRecordEncoder)


@app.route('/stop')
def stop():
    sid = request.args.get('sid')
    thread = threads[sid]
    thread.stop()
    logger.info('Wipe stopped for %s', sid)
    WebHandler.clear_logs(sid)
    return jsonify({'status': 'stopped'})
