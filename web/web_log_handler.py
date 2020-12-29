import json
from logging import LogRecord, StreamHandler
from typing import List

import attr


@attr.s
class WipeLogRecord(object):
    msg: str = attr.ib()
    level: str = attr.ib()
    timestamp: int = attr.ib()


class WipeLogRecordEncoder(json.JSONEncoder):

    def default(self, obj: WipeLogRecord) -> dict:
        return {
            'msg': obj.msg,
            'level': obj.level,
            'timestamp': obj.timestamp,
        }


class WebLogHandler(StreamHandler):
    logs: List[WipeLogRecord] = []

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)

        w_record = WipeLogRecord(
            msg=f'{record.threadName} {msg}',
            level=record.levelname,
            timestamp=int(record.created * 1000),
        )

        self.logs.append(w_record)
        super().emit(record)

    @classmethod
    def get_logs(cls, user_id: str):
        logs = cls.logs
        logs.sort(key=lambda obj: obj.timestamp, reverse=True)
        return logs

    @classmethod
    def clear_logs(cls, user_id: str):
        cls.logs = []
