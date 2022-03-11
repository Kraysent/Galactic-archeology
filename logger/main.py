from typing import Tuple
import logger.logger as logger
from logger.config import Config
import numpy as np


def initialize(config: Config):
    for log in config.handlers:
        if log.handler_type == 'console':
            logger.add_console_handler(**log.args)
        elif log.handler_type == 'file':
            logger.add_file_handler(**log.args)
        elif log.handler_type == 'json':
            logger.add_json_handler(**log.args)

def info(msg: str):
    logger.get_instance().info(msg)

def debug(msg: str):
    logger.get_instance().debug(msg)

def warning(msg: str):
    logger.get_instance().warning(msg)

def error(msg: str):
    logger.get_instance().error(msg)

def run_handler(data: Tuple[np.ndarray, np.ndarray], parameters: dict = {}):
    if parameters['print_last']:
        info(f'x: {data[0].tolist()[-1]}, y: {data[1].tolist()[-1]}')
    else:
        info(f'x: {data[0].tolist()}, y: {data[1].tolist()}')