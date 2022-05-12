"""
Struct that holds abstract_task, its part and handlers.
"""
from typing import Callable, Tuple

import numpy as np

from omtool.core.datamodel.abstract_task import AbstractTask
from omtool.core.datamodel.snapshot import Snapshot


class HandlerTask:
    """
    Struct that holds abstract_task, its part and handlers.
    """

    def __init__(
        self,
        task: AbstractTask,
        part=slice(0, None),
        handlers: list[Callable[[Tuple[np.ndarray, np.ndarray]], None]] = None,
    ):
        if handlers is None:
            handlers = []

        self.task = task
        self.part = part
        self.handlers = handlers

    def run(self, snapshot: Snapshot):
        """
        Launch the task and return its value
        """
        data = self.task.run(snapshot[self.part])

        for handler in self.handlers:
            handler(data)
