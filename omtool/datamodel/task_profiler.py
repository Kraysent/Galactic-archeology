import time
from typing import Any, Dict, List

import numpy as np

instance = None

def _get_instance() -> 'profilerSingleton':
    global instance 

    if instance is None:
        instance = profilerSingleton()

    return instance

def add_value(key, value):
    _get_instance().add_value(key, value)

def dump_times() -> Dict[Any, float]:
    return _get_instance().dump_times()

class profilerSingleton:
    def __init__(self):
        self.times: Dict[Any, List[float]] = {}

    def add_value(self, key, value):
        if not key in self.times:
            self.times[key] = []

        self.times[key].append(value)

    def dump_times(self) -> Dict[Any, float]:
        res = {}

        for key, val in self.times.items():
            res[key] = np.average(val)

        return res

class profiler:
    def __init__(self, name = ''):
        self.name = name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            result_time = time.time() - start
            
            if self.name == '':
                self.name = func.__qualname__

            add_value(self.name, result_time)

            return res
    
        return wrapper
