from omtool.analysis.tasks import AbstractTask
from omtool.datamodel import Snapshot

class VisualTask:
    def __init__(self, 
        axes_id: int, 
        task: AbstractTask,
        part = slice(0, None),
        handlers: dict = {}
    ):
        self.axes_id = axes_id
        self.task = task
        self.part = part
        self.handlers = handlers

    def get_active_snapshot(self, snapshot: Snapshot):
        return snapshot[self.part]

    def run(self, snapshot: Snapshot):
        return self.task.run(self.get_active_snapshot(snapshot))