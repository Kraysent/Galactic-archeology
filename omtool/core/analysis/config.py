"""
Configuration classes for analysis tool.
"""
from typing import Any, List

import yaml
from omtool import io_service, visualizer
from omtool.tasks import get_task
from omtool.core.datamodel import required_get, yaml_loader


class TaskConfig:
    """
    Configuration for each particular task.
    """

    slice: slice
    abstract_task: Any  # AbstractTask actually
    handlers: dict

    @staticmethod
    def from_dict(data: dict) -> "TaskConfig":
        """
        Construct this object from dictionary.
        """
        res = TaskConfig()
        res.slice = slice(*data.get("slice", [0, None, 1]))
        res.handlers = data.get("handlers", {})
        res.abstract_task = get_task(required_get(data, "name"), data.get("args", {}))

        return res


class AnalysisConfig:
    """
    General configuration for analysis tool.
    """

    input_file: io_service.Config
    visualizer: visualizer.Config
    tasks: List[TaskConfig]

    @staticmethod
    def from_yaml(filename: str) -> "AnalysisConfig":
        """
        Construct this object from YAML file.
        """
        data = {}

        with open(filename, "r", encoding="utf-8") as stream:
            data = yaml.load(stream, Loader=yaml_loader())

        return AnalysisConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "AnalysisConfig":
        """
        Construct this object from dictionary.
        """
        res = AnalysisConfig()
        res.tasks = [TaskConfig.from_dict(task) for task in data.get("tasks", [])]

        res.visualizer = data.get("visualizer", None)
        if not res.visualizer is None:
            res.visualizer = visualizer.Config.from_dict(res.visualizer)

        res.input_file = io_service.Config.from_dict(required_get(data, "input_file"))

        return res
