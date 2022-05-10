from omtool.core.analysis.tasks import AbstractTask
from omtool.core.datamodel import Snapshot


class VisualTask:
    """
    Struct that holds abstract_task, its part and handlers.
    """

    def __init__(
        self,
        task: AbstractTask,
        part=slice(0, None),
        handlers: dict = None,
    ):
        if handlers is None:
            handlers = {}

        self.task = task
        self.part = part
        self.handlers = handlers

    def run(self, snapshot: Snapshot):
        """
        Launch the task and return its value
        """
        return self.task.run(snapshot[self.part])
