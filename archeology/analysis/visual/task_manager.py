from archeology.analysis.visual.visual_task import VisualTask


class TaskManager:
    def __init__(self) -> None:
        self.tasks = []

    def add_tasks(self, *visual_tasks):
        vtask: VisualTask
        for vtask in visual_tasks:
            self.tasks.append(vtask)

    def get_tasks(self) -> list[VisualTask]:
        return self.tasks
