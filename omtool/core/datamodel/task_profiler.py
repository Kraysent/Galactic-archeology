'''
Description of the profiler decorator and accompanying methods.
'''
# pylint: disable=invalid-name,global-statement
# Since profiler is decorator, pylint does not understand
# the naming convention for it.
# Also profiler is singleton so it needs global statement.
import time
from collections import namedtuple
from typing import Any, Dict

import numpy as np

_profiler_singleton = namedtuple('profiler_singleton', 'times')
_instance: _profiler_singleton = None

def _get_instance() -> _profiler_singleton:
    global _instance

    if _instance is None:
        _instance = _profiler_singleton(times = {})

    return _instance

def _add_value(key, value):
    instance = _get_instance()

    if not key in instance.times:
        instance.times[key] = []

    instance.times[key].append(value)

def dump_times() -> Dict[Any, float]:
    '''
    Average out all the values and return them as a dictionary.
    '''
    instance = _get_instance()
    res = {}

    for key, val in instance.times.items():
        res[key] = np.average(val)

    return res

class profiler:
    '''
    Decorator that enables profiling of the certain function.
    '''
    def __init__(self, name = ''):
        self.name = name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            result_time = time.time() - start

            if self.name == '':
                self.name = func.__qualname__

            _add_value(self.name, result_time)

            return res

        return wrapper
