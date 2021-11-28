from archeology.analysis.tasks import AbstractTask
from archeology.analysis.visual.plot_parameters import DrawParameters
from archeology.datamodel import Snapshot

class VisualTask:
    def __init__(self, 
        axes_id: int, 
        task: AbstractTask,
        part = slice(0, None),
        draw_params: DrawParameters = DrawParameters()
    ):
        self.axes_id = axes_id
        self.task = task
        self.part = part
        self.draw_params = draw_params


    def get_active_snapshot(self, snapshot: Snapshot):
        return snapshot[self.part]

    def run(self, snapshot: Snapshot):
        return self.task.run(self.get_active_snapshot(snapshot))