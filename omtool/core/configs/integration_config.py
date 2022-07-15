from dataclasses import dataclass
from typing import Any, Optional

from amuse.lab import ScalarQuantity
from marshmallow import Schema, fields, post_load

import omtool.json_logger as logger
from omtool import io_service, tasks, visualizer


@dataclass
class Integrator:
    name: str
    args: dict[str, Any]


@dataclass
class LogParams:
    point_id: int
    logger_id: str


@dataclass
class IntegrationConfig:
    input_file: io_service.Config
    output_file: str
    overwrite: bool
    model_time: ScalarQuantity
    integrator: Integrator
    logging: logger.Config
    snapshot_interval: int
    visualizer: Optional[visualizer.Config]
    tasks: list[tasks.Config]
    logs: list[LogParams]


class IntegratorSchema(Schema):
    name = fields.Str(required=True)
    args = fields.Dict(fields.Str(), required=True)

    @post_load
    def make(self, data, **kwargs):
        return Integrator(**data)


class LogParamsSchema(Schema):
    point_id = fields.Int(required=True)
    logger_id = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        return LogParams(**data)


class IntegrationConfigSchema(Schema):
    input_file = fields.Nested(io_service.IOConfigSchema, required=True)
    output_file = fields.Str(required=True)
    overwrite = fields.Bool(load_default=False)
    model_time = fields.Raw(required=True)
    integrator = fields.Nested(IntegratorSchema, required=True)
    snapshot_interval = fields.Int(load_default=1)
    logging = fields.Nested(logger.LoggerConfigSchema)
    visualizer = fields.Nested(visualizer.VisualizerConfigSchema, load_default=None)
    tasks = fields.List(fields.Nested(tasks.TasksConfigSchema), load_default=[])
    logs = fields.List(fields.Nested(LogParamsSchema), load_default=[])

    @post_load
    def make(self, data: dict, **kwargs):
        return IntegrationConfig(**data)
