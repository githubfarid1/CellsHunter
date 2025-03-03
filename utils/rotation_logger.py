import logging
import pathlib
from logging import Filter
from logging import LogRecord
from logging.handlers import RotatingFileHandler

log_lvl = logging.DEBUG

# formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s.%(funcName)s(%(lineno)d) - %(message)s')
formatter = logging.Formatter('%(levelname)s %(asctime)s [%(funcName)s(%(lineno)s)] | MSG: %(message)s')

log_path = pathlib.Path('logs')
if not log_path.exists():
    log_path.mkdir(exist_ok=True, parents=True)

log_file = log_path.joinpath('logs.log')

log_rotate = RotatingFileHandler(
    filename=log_file, mode='a', encoding='utf-8', maxBytes=256000, backupCount=3, delay=True)  # 256kb
log_rotate.setLevel(log_lvl)
log_rotate.setFormatter(formatter)


# errors_filter = ErrorsFilter()
# log_rotate.addFilter(errors_filter)

class ErrorsFilter(Filter):

    def filter(self, record: LogRecord) -> bool:
        if record.levelno >= logging.WARNING:
            return True
        return False


class InfoFilter(Filter):

    def filter(self, record: LogRecord) -> bool:
        if logging.WARNING > record.levelno >= logging.DEBUG:
            return True
        return False


def setup_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.addHandler(log_rotate)
    logger.setLevel(log_lvl)
    return logger
