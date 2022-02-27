import logging

_instance = None

def get_instance() -> 'Logger':
    global _instance

    if _instance is None:
        _instance = Logger()
        _instance.logger = logging.getLogger('OMTool')
        _instance.logger.setLevel(logging.DEBUG)
        fh = logging.StreamHandler()
        fh_formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(message)s', '%H:%M:%S')
        fh.setFormatter(fh_formatter)
        _instance.logger.addHandler(fh)

    return _instance

def info(msg: str):
    get_instance().info(msg)

def debug(msg: str):
    get_instance().logger.debug(msg)

class Logger:
    logger: logging.Logger

    def info(self, msg: str):
        self.logger.info(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)
