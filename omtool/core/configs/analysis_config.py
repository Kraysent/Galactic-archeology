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

    input_file = fields.Nested(io_service.ConfigSchema, required=True)
    visualizer = fields.Nested(visualizer.ConfigSchema, load_default=None)
    tasks = fields.List(fields.Nested(tasks.ConfigSchema), load_default=[])
    logging = fields.Nested(logger.ConfigSchema)

    @post_load
    def make(self, data: dict, **kwargs):
        return AnalysisConfig(**data)
