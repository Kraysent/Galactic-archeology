from omtool import visualizer
from omtool.core.tasks import DataType


class VisualizerAction:
    def __init__(self, service: visualizer.VisualizerService):
        self.service = service

    def __call__(self, data: DataType, **parameters) -> DataType:
        self.service.plot(data, parameters)

        return data
