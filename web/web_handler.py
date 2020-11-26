from logging import Handler, LogRecord, StreamHandler

LOGS = []  # noqa: WPS407


class WebHandler(StreamHandler):

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        LOGS.append({
            'msg': msg,
            'level': record.levelname
        })
