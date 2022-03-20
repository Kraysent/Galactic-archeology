from omtool.analysis.tasks import AbstractTask
from omtool.datamodel import Snapshot


class VisualTask:
    '''
    Struct that holds abstract_task, its part and visual parameters.
    '''

    def __init__(self,
                 axes_id: int,
                 task: AbstractTask,
                 part=slice(0, None),
                 handlers: dict = None
                 ):
        if handlers is None:
            handlers = {}

        self.axes_id = axes_id
        self.task = task
        self.part = part
        self.handlers = handlers

    def run(self, snapshot: Snapshot):
        '''
        Launch the task and return its value
        '''
        return self.task.run(snapshot[self.part])
