import json
from dataclasses import dataclass
from logging import Formatter, LogRecord, StreamHandler
from typing import List


@dataclass
class WipeLogRecord(object):
    msg: str
    level: str
    timestamp: int


class WipeLogRecordEncoder(json.JSONEncoder):

    def default(self, obj: WipeLogRecord) -> dict:
        return {
            'msg': obj.msg,
            'level': obj.level,
            'timestamp': obj.timestamp,
        }


class WipeLogHandler(StreamHandler):
    logs: List[WipeLogRecord] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = Formatter(fmt='%(threadName)s %(asctime)s: %(message)s', datefmt='%H:%M:%S')

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)

        w_record = WipeLogRecord(
            msg=msg,
            level=record.levelname,
            timestamp=int(record.created * 1000),
        )

        self.logs.append(w_record)

    def get_logs(self):
        logs = self.logs
        logs.sort(key=lambda obj: obj.timestamp, reverse=True)
        return logs

    def clear_logs(self):
        self.logs.clear()
