"""
Struct that holds abstract_task, its part and actions.
"""
from typing import Callable, Tuple

import numpy as np

from omtool.core.datamodel.abstract_task import AbstractTask
from omtool.core.datamodel.snapshot import Snapshot

DataType = Tuple[np.ndarray, np.ndarray]


class HandlerTask:
    """
    Struct that holds abstract_task, its part and actions.
    """

    def __init__(
        self,
        task: AbstractTask,
        actions_before: list[Callable[[Snapshot], Snapshot]] = None,
        actions_after: list[Callable[[DataType], DataType]] = None,
    ):
        if actions_before is None:
            actions_before = []

        if actions_after is None:
            actions_after = []

        self.task = task
        self.actions_before = actions_before
        self.actions_after = actions_after

    def run(self, snapshot: Snapshot):
        """
        Run actions before, launch task, run actions after.
        """
        for action in self.actions_before:
            snapshot = action(snapshot)

        data = self.task.run(snapshot)

        for handler in self.actions_after:
            data = handler(data)
