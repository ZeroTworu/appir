from logging import Handler, LogRecord

from web.main import LOGS


class WebHandler(Handler):

    def emit(self, record: LogRecord) -> None:
        LOGS.append(record)
