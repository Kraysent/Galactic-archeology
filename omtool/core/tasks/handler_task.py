from typing import Callable

from omtool.core.datamodel.snapshot import Snapshot
from omtool.core.tasks.abstract_task import AbstractTask, DataType


class HandlerTask:
    """
    Struct that holds abstract_task and its actions.
    """

    def __init__(
        self,
        task: AbstractTask,
        inputs: dict[str, str] | None = None,
        actions_before: list[Callable[[Snapshot], Snapshot]] | None = None,
        actions_after: list[Callable[[DataType], DataType]] | None = None,
    ):
        inputs = inputs or {}
        actions_before = actions_before or []
        actions_after = actions_after or []

        self.task = task
        self.inputs = inputs
        self.actions_before = actions_before
        self.actions_after = actions_after

    def run(self, snapshot: Snapshot, previous_outputs: dict[str, DataType]) -> DataType:
        """
        Run actions before, launch task, run actions after.
        """
        for action_before in self.actions_before:
            snapshot = action_before(snapshot)

        kwargs = {}

        for key, path in self.inputs.items():
            task_id, value_id = path.split(".")
            kwargs[key] = previous_outputs[task_id][value_id]

        data = self.task.run(snapshot, **kwargs)

        for action_after in self.actions_after:
            data = action_after(data)

        return data
