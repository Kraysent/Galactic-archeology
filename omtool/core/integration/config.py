"""
Confuration objects' description for integration module.
"""
from typing import List
import yaml

from amuse.lab import ScalarQuantity
from omtool import io_service, tasks
from omtool.core.utils import required_get, yaml_loader
from omtool import visualizer


class LogParamsConfig:
    """
    Configuration of logging parameters for particles.
    """

    point_id: int
    logger_id: str

    @staticmethod
    def from_dict(data: dict) -> "LogParamsConfig":
        """
        Loads this type from dictionary.
        """
        res = LogParamsConfig()
        res.point_id = required_get(data, "point_id")
        res.logger_id = required_get(data, "logger_id")

        return res


class IntegratorConfig:
    """
    Configuration for the particular integrator.
    """

    name: str
    args: dict

    @staticmethod
    def from_dict(data: dict) -> "IntegratorConfig":
        """
        Loads this type from dictionary.
        """
        res = IntegratorConfig()
        res.name = required_get(data, "name")
        res.args = data.get("args", {})

        return res


class IntegrationConfig:
    """
    General configuration for integration.
    """

    input_file: io_service.Config
    output_file: str
    overwrite: bool
    model_time: ScalarQuantity
    snapshot_interval: int
    integrator: IntegratorConfig
    logs: List[LogParamsConfig]
    visualizer: visualizer.Config
    tasks: List[tasks.Config]

    @staticmethod
    def from_yaml(filename: str) -> "IntegrationConfig":
        """
        Loads this type from the actual YAML file.
        """
        data = {}

        with open(filename, "r", encoding="utf-8") as stream:
            data = yaml.load(stream, Loader=yaml_loader())

        return IntegrationConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "IntegrationConfig":
        """
        Loads this type from dictionary.
        """
        res = IntegrationConfig()
        res.input_file = io_service.Config.from_dict(required_get(data, "input_file"))
        res.output_file = required_get(data, "output_file")
        res.overwrite = data.get("overwrite", False)
        res.model_time = required_get(data, "model_time")
        res.snapshot_interval = data.get("snapshot_interval", 1)
        res.integrator = IntegratorConfig.from_dict(required_get(data, "integrator"))
        res.logs = [LogParamsConfig.from_dict(log) for log in data.get("logs", [])]
        res.tasks = [tasks.Config.from_dict(task) for task in data.get("tasks", [])]

        res.visualizer = data.get("visualizer", None)
        if not res.visualizer is None:
            res.visualizer = visualizer.Config.from_dict(res.visualizer)

        return res
