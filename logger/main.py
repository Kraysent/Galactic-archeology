'''
Logger service that provides functionality to print logs
into different destinations.
'''
from typing import Tuple
import numpy as np
from logger import logger
from logger.config import Config


def initialize(config: Config):
    '''
    Load the logger from config.
    '''
    for log in config.handlers:
        if log.handler_type == 'console':
            logger.add_console_handler(**log.args)
        elif log.handler_type == 'file':
            logger.add_file_handler(**log.args)
        elif log.handler_type == 'json':
            logger.add_json_handler(**log.args)


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


def run_handler(data: Tuple[np.ndarray, np.ndarray], parameters: dict = None):
    '''
    Handler that logs ndarrays to the INFO level.
    '''
    if parameters is None:
        parameters = {}

    if parameters['print_last']:
        info(f'x: {data[0].tolist()[-1]}, y: {data[1].tolist()[-1]}')
    else:
        info(f'x: {data[0].tolist()}, y: {data[1].tolist()}')
