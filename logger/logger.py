'''
Methods to create new handlers for the logger.
'''
import logging
import sys
import json

_instance = None


def get_instance() -> logging.Logger:
    '''
    Returns instance of the logger or creates new one if no instance
    was created before.
    '''
    global _instance

    if _instance is None:
        _instance = logging.getLogger('OMTool')
        _instance.setLevel(logging.DEBUG)

    return _instance


def add_console_handler(fmt: str, stream='stderr', datefmt: str = '%H:%M:%S'):
    '''
    Add new handler that prints logs into the console.
    '''
    stream_names = {
        'stderr': sys.stderr,
        'stdout': sys.stdout
    }
    handler = logging.StreamHandler(stream_names.get(stream, sys.stderr))
    formatter = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formatter)
    get_instance().addHandler(handler)


def add_file_handler(fmt: str, filename: str, datefmt: str = '%H:%M:%S'):
    '''
    Add new handler that prints logs to the file.
    '''
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formatter)
    get_instance().addHandler(handler)


def add_json_handler(filename: str, datefmt: str = '%H:%M:%S'):
    '''
    Add new handler that saves logs into the JSON file.
    '''
    handler = logging.FileHandler(filename)
    format_dict = {
        'time': '%(asctime)s',
        'level': '%(levelname)s',
        'message': '%(message)s'
    }
    formatter = logging.Formatter(json.dumps(format_dict), datefmt)
    handler.setFormatter(formatter)
    get_instance().addHandler(handler)
