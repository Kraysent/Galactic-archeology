import omtool.json_logger.logger as logger
from omtool.json_logger.config import Config

def initialize(config: Config):
    '''
    Initialize JSON logger with paramaters.
    '''
    logger.add_json_handler(config.filename, datefmt=config.datefmt)

def info(msg: str = '', message_type: str = 'msg', payload: dict = None):
    '''
    Push log message of the INFO level.
    '''
    if payload is None:
        payload = {}

    if message_type == 'msg':
        payload['message'] = msg

    logger.get_instance().info('', extra = {'message_type': message_type, 'data': payload})


def debug(msg: str = '', message_type: str = 'msg', payload: dict = None):
    '''
    Push log message of the DEBUG level.
    '''
    if payload is None:
        payload = {}

    if message_type == 'msg':
        payload['message'] = msg

    logger.get_instance().debug('', extra = {'message_type': message_type, 'data': payload})

def warning(msg: str = '', message_type: str = 'msg', payload: dict = None):
    '''
    Push log message of the WARNING level.
    '''
    if payload is None:
        payload = {}

    if message_type == 'msg':
        payload['message'] = msg

    logger.get_instance().warning('', extra = {'message_type': message_type, 'data': payload})

def error(msg: str = '', message_type: str = 'msg', payload: dict = None):
    '''
    Push log message of the ERROR level.
    '''
    if payload is None:
        payload = {}

    if message_type == 'msg':
        payload['message'] = msg

    logger.get_instance().error('', extra = {'message_type': message_type, 'data': payload})
