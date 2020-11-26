import logging
from typing import List

from flask import Flask, jsonify, redirect, render_template, request
from wipe import STRATEGIES, __version__
from wipe.wipe import WipeParams

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

app = Flask(__name__)

LOGS = []


def validate(form_data: dict) -> List[str]:
    errors = []
    if form_data.get('room_url', None) is None:
        errors.append('Не указан адрес конфы')
    if form_data.get('wipe_type') == 'youtube' and form_data.get('youtube_url', None) is None:  # noqa: WPS221
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
        others_params={'link': form_data.get('youtube_url', None)},
    )

    strategy = strategy_class(wipe_params)
    strategy.register_event_callback(lambda x: LOGS.append(x))
    strategy.run_strategy()


@app.route('/')
def hello_world(errors=None, infos=None):
    params = {
        'version': __version__,
        'strategies': STRATEGIES,
        'errors': [] if errors is None else errors,
        'infos': [] if infos is None else infos,
    }
    return render_template('index.html', **params)


@app.route('/wipe', methods=['POST'])
def wipe():
    form_data = request.form
    errors = validate(form_data)
    if bool(errors):
        return hello_world(errors=errors)
    run_wipe(form_data)
    return redirect('/')


@app.route('/status')
def status():
    if bool(LOGS):
        return jsonify(
            log=LOGS.pop()
        )
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=False)
