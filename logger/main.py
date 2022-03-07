import logger.logger as logger
from logger.config import Config


def initialize(config: Config):
    for log in config.handlers:
        if log.handler_type == 'console':
            logger.add_console_handler(**log.args)
        elif log.handler_type == 'file':
            logger.add_file_handler(**log.args)

def info(msg: str):
    logger.get_instance().info(msg)

def debug(msg: str):
    logger.get_instance().debug(msg)

def warning(msg: str):
    logger.get_instance().warning(msg)

def error(msg: str):
    logger.get_instance().error(msg)
