from dataclasses import dataclass
from typing import Optional

from marshmallow import EXCLUDE, Schema, fields, post_load

import omtool.json_logger as logger
from omtool import io_service, tasks, visualizer


@dataclass
class AnalysisConfig:
    input_file: io_service.Config
    visualizer: Optional[visualizer.Config]
    tasks: list[tasks.Config]
    logging: logger.Config


class AnalysisConfigSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    input_file = fields.Nested(io_service.IOConfigSchema, required=True)
    visualizer = fields.Nested(visualizer.VisualizerConfigSchema, load_default=None)
    tasks = fields.List(fields.Nested(tasks.TasksConfigSchema), load_default=[])
    logging = fields.Nested(logger.LoggerConfigSchema, description="Pictures will be saved in output_dir with this filename. i is iteration number.")

    @post_load
    def make(self, data: dict, **kwargs):
        return AnalysisConfig(**data)
