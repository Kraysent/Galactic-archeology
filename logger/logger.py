import logging
import sys

_instance = None

def get_instance() -> logging.Logger:
    global _instance

    if _instance is None:
        _instance = logging.getLogger('OMTool')
        _instance.setLevel(logging.DEBUG)

    return _instance

def add_console_handler(format: str, stream = 'stderr', datefmt: str = '%H:%M:%S'):
    stream_names = {
        'stderr': sys.stderr,
        'stdout': sys.stdout
    }
    handler = logging.StreamHandler(stream_names.get(stream, sys.stderr))
    formatter = logging.Formatter(format, datefmt)
    handler.setFormatter(formatter)
    get_instance().addHandler(handler)

def add_file_handler(format: str, filename: str, datefmt: str = '%H:%M:%S'):
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter(format, datefmt)
    handler.setFormatter(formatter)
    get_instance().addHandler(handler)

