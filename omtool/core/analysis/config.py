"""
Configuration classes for analysis tool.
"""
from typing import List

import yaml

from omtool import io_service, tasks, visualizer
from omtool.core.utils import required_get, yaml_loader


class AnalysisConfig:
    """
    General configuration for analysis tool.
    """

    input_file: io_service.Config
    visualizer: visualizer.Config
    tasks: List[tasks.Config]

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
        res.tasks = [tasks.Config.from_dict(task) for task in data.get("tasks", [])]

        res.visualizer = data.get("visualizer", None)
        if res.visualizer is not None:
            res.visualizer = visualizer.Config.from_dict(res.visualizer)

        res.input_file = io_service.Config.from_dict(required_get(data, "input_file"))

        return res
