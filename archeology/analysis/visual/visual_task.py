from typing import Any, Callable
from archeology.analysis.tasks import AbstractTask
from archeology.analysis.visual.plot_parameters import DrawParameters
from archeology.datamodel import Snapshot

class VisualTask:
    def __init__(self, 
        axes_id: int, 
        task: AbstractTask,
        part = slice(0, None),
        draw_params: DrawParameters = DrawParameters(),
        action: Callable[[Snapshot], Any] = None
    ):
        self.axes_id = axes_id
        self.task = task
        self.part = part
        self.draw_params = draw_params
        self.action = action

    def get_active_snapshot(self, snapshot: Snapshot):
        if isinstance(self.part, slice):
            return snapshot[self.part]
        elif isinstance(self.part, tuple):
            total = snapshot[self.part[0]]

            for i in range(1, len(self.part)):
                total.add(snapshot[self.part[i]])

            return total
        else:
            raise RuntimeError('Unknown slicing type')

    def run(self, snapshot: Snapshot):
        if self.action is not None:
            self.action(snapshot)
        
        return self.task.run(self.get_active_snapshot(snapshot))