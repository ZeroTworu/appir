import json
import logging
import uuid
from typing import List

from flask import Flask, jsonify, render_template, request
from flask_classy import FlaskView, route
from web.web_log_handler import WebLogHandler, WipeLogRecordEncoder
from wipe import __version__
from wipe.params import PreparedStrategy, WipeParams
from wipe.strategies import STRATEGIES
from wipe.threads import WipeThreadManager

app = Flask(__name__)

logging.basicConfig(format='%(threadName)s-%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
wh = WebLogHandler()
logger.addHandler(wh)

flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.ERROR)


def validate(form_data) -> List[str]:
    errors = []
    if form_data.get('room_url', '') == '':
        errors.append('Не указан адрес конфы')
    if form_data.get('wipe_type') == 'youtube' and form_data.get('youtube_url', '') == '':  # noqa: WPS221
        errors.append('Выбран вайп ютубом, но не указана ссылка на ролик')
    return errors


class WebHandler(FlaskView):
    route_base = '/'

    def __init__(self):
        self.manager = None
        self.form_data = None

    def index(self):
        params = {
            'version': __version__,
            'strategies': STRATEGIES,
            'sid': f'{uuid.uuid4()}',
        }
        return render_template('index.html', **params)

    @route('/wipe/', methods=['POST'])
    def wipe(self):
        self.form_data = request.json
        errors = validate(self.form_data)
        if bool(errors):
            return jsonify({'status': 'error', 'errors': errors})

        strategy_class = STRATEGIES.get(self.form_data['wipe_type'], None)

        if strategy_class is None:
            logging.error('Wrong strategy %s, write it by you self!', self.form_data['wipe_type'])
            return jsonify({'status': 'error'})

        wipe_params = WipeParams(
            room_url=self.form_data['room_url'],
            sid=self.form_data['sid'],
            browser=self.form_data['browser'],
            fake_media=self.form_data.get('fake_media', 'off') == 'on',
            headless=True,
            others_params={'link': self.form_data.get('youtube_url', None)},
            logger=logger,
        )

        strategy = PreparedStrategy(params=wipe_params, strategy_class=strategy_class)
        self.manager = WipeThreadManager(strategy=strategy, threads_count=int(self.form_data.get('threads', 1)))
        self.manager.start()
        return jsonify({'status': 'started'})

    @route('/status/<sid>')
    def status(self, sid):
        logs = WebLogHandler.get_logs(sid)
        return json.dumps(logs, cls=WipeLogRecordEncoder)

    @route('/stop/<sid>')
    def stop(self, sid):
        self.manager.stop()
        logger.info('Wipe stopped for %s', sid)
        WebLogHandler.clear_logs(sid)
        return jsonify({'status': 'stopped'})


WebHandler.register(app)
