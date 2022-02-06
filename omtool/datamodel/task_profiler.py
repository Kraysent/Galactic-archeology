from functools import wraps
import time
from typing import Any, Dict, List
import numpy as np

instance = None

class ProfilerSingleton:
    def __init__(self):
        self.times: Dict[Any, List[float]] = {}
        self.instance = self

    @staticmethod
    def get_instance() -> 'ProfilerSingleton':
        global instance 

        if instance is None:
            instance = ProfilerSingleton()

        return instance

    def add_value(self, key, value):
        if not key in self.times:
            self.times[key] = []

        self.times[key].append(value)

    def dump_times(self) -> Dict[Any, float]:
        res = {}

        for key, val in self.times.items():
            res[key] = np.average(val)

        return res

def profiler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        result_time = time.time() - start
        
        profiler_instance = ProfilerSingleton.get_instance()
        profiler_instance.add_value(func.__qualname__, result_time)

        return res
    
    return wrapper
