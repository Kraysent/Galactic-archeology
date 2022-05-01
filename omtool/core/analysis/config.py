from typing import Any, List

from omtool import io_service
from omtool import visualizer
import yaml
from omtool.core.analysis.tasks import get_task
from omtool.core.datamodel import required_get, yaml_loader


class TaskConfig:
    slice: slice
    abstract_task: Any # AbstractTask actually
    handlers: dict
    
    @staticmethod
    def from_dict(input: dict) -> 'TaskConfig':
        res = TaskConfig()
        res.slice = slice(*input.get('slice', [0, None, 1]))
        res.handlers = input.get('handlers', { })
        res.abstract_task = get_task(
            required_get(input, 'name'), 
            input.get('args', { })
        )

        return res

class AnalysisConfig:
    input_file: io_service.Config
    visualizer: visualizer.Config
    tasks: List[TaskConfig]
    plot_interval: slice

    @staticmethod
    def from_yaml(filename: str) -> 'AnalysisConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())
        
        return AnalysisConfig.from_dict(data)

    @staticmethod
    def from_dict(input: dict) -> 'AnalysisConfig':
        res = AnalysisConfig()
        res.tasks = [
            TaskConfig.from_dict(task) for task in required_get(input, 'tasks')
        ]
        res.plot_interval = slice(*input.get('plot_interval', [0, None, 1]))
        res.visualizer = visualizer.Config.from_dict(required_get(input, 'visualizer'))
        res.input_file = io_service.Config.from_dict(required_get(input, 'input_file'))

        return res

