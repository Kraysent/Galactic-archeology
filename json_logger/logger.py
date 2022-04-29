import json
import logging
import sys


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

def add_json_handler(filename: str = '', datefmt: str = '%H:%M:%S', stream: str = 'stderr'):
    '''
    Add new handler that saves logs into the JSON file.
    '''
    format_dict = {
        'time': '%(asctime)s',
        'level': '%(levelname)s',
        'message_type': '%(message_type)s',
        'data': '%(data)s'
    }

    if filename != '':
        file_handler = logging.FileHandler(filename)
        file_formatter = logging.Formatter(json.dumps(format_dict), datefmt)
        file_handler.setFormatter(file_formatter)
        get_instance().addHandler(file_handler)

    stream_names = {
        'stderr': sys.stderr,
        'stdout': sys.stdout
    }
    console_handler = logging.StreamHandler(stream_names.get(stream, sys.stderr))
    console_formatter = logging.Formatter(json.dumps(format_dict), datefmt)
    console_handler.setFormatter(console_formatter)
    get_instance().addHandler(console_handler)
