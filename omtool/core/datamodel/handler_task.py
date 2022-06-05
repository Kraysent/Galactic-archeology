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
        actions_before: list[Callable[[Snapshot], Snapshot]] = None,
        handlers: list[Callable[[Tuple[np.ndarray, np.ndarray]], None]] = None,
    ):
        if actions_before is None:
            actions_before = []

        if handlers is None:
            handlers = []

        self.task = task
        self.actions_before = actions_before
        self.handlers = handlers

    def run(self, snapshot: Snapshot):
        """
        Launch the task and return its value
        """
        for action in self.actions_before:
            snapshot = action(snapshot)

        data = self.task.run(snapshot)

        for handler in self.handlers:
            handler(data)
