import json_logger.logger as logger
from json_logger.config import Config

def initialize(config: Config):
    '''
    Initialize JSON logger with paramaters.
    '''
    logger.add_json_handler(config.filename)


def info(msg: str):
    '''
    Push log message of the INFO level.
    '''
    logger.get_instance().info(msg)


def debug(msg: str):
    '''
    Push log message of the DEBUG level.
    '''
    logger.get_instance().debug(msg)


def warning(msg: str):
    '''
    Push log message of the WARNING level.
    '''
    logger.get_instance().warning(msg)


def error(msg: str):
    '''
    Push log message of the ERROR level.
    '''
    logger.get_instance().error(msg)
