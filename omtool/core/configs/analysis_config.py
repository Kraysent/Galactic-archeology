from dataclasses import dataclass
from typing import Optional

from omtool import visualizer
from omtool.core import tasks
from omtool.core.configs.base_config import BaseConfig
from omtool.core.configs.input_config import InputConfig


@dataclass
class AnalysisConfig(BaseConfig):
    input_file: InputConfig
    visualizer: Optional[visualizer.VisualizerConfig]
    tasks: list[tasks.TasksConfig]
