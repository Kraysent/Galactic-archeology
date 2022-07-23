from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from amuse.lab import ScalarQuantity
from marshmallow import Schema, fields, post_load

from omtool import io_service, tasks, visualizer
from omtool.core.configs.base_config import BaseConfig, BaseSchema


@dataclass
class Integrator:
    name: str
    args: dict[str, Any]


@dataclass
class LogParams:
    point_id: int
    logger_id: str


@dataclass
class IntegrationConfig(BaseConfig):
    input_file: io_service.Config
    output_file: str
    overwrite: bool
    model_time: ScalarQuantity
    integrator: Integrator
    snapshot_interval: int
    visualizer: Optional[visualizer.Config]
    tasks: list[tasks.Config]
    logs: list[LogParams]


class IntegratorSchema(Schema):
    name = fields.Str(required=True, description="Name of the integrator.")
    args = fields.Dict(
        fields.Str(),
        required=True,
        description="Arguments that would be passed into the constructur of the integrator.",
    )

    @post_load
    def make(self, data, **kwargs):
        return Integrator(**data)


class LogParamsSchema(Schema):
    point_id = fields.Int(required=True, description="ID of particle from the model.")
    logger_id = fields.Str(required=True, description="ID of logger.")

    @post_load
    def make(self, data, **kwargs):
        return LogParams(**data)


class IntegrationConfigSchema(BaseSchema):
    input_file = fields.Nested(
        io_service.IOConfigSchema,
        required=True,
        description="Parameters of input file: its format and path.",
    )
    output_file = fields.Str(
        required=True, description="Path to file where output model would be saved."
    )
    overwrite = fields.Bool(
        load_default=False,
        description="Flag that shows whether to overwrite model if it already exists "
        "on given filepath.",
    )
    model_time = fields.Raw(
        required=True,
        type="array",
        description="Time until which model would be integrated. In future custom conditition "
        "is planned to be applied.",
    )
    integrator = fields.Nested(
        IntegratorSchema,
        required=True,
        description="Object that stores infromation about the integration algorithm.",
    )
    snapshot_interval = fields.Int(
        load_default=1,
        description="Interval between to consecutive snapshots to write to output file.",
    )
    visualizer = fields.Nested(
        visualizer.VisualizerConfigSchema,
        load_default=None,
        description="Visualizer is responsible for the matplotlib's plots, their layout and format "
        "of the data. This fields describes layout; format of the data is specified inside tasks.",
    )
    tasks = fields.List(
        fields.Nested(tasks.TasksConfigSchema),
        load_default=[],
        description="This field describes list of tasks. Each task is a class that has run(...) "
        "method that processes Snapshot and returns some data.",
    )
    logs = fields.List(
        fields.Nested(LogParamsSchema),
        load_default=[],
        description="List of particles which parameters would be written to log file.",
    )

    @post_load
    def make(self, data: dict, **kwargs):
        if not data["overwrite"] and Path(data["output_file"]).is_file():
            raise FileExistsError(
                f'Output file ({data["output_file"]}) exists and "overwrite" '
                "option in integration config file is false (default)"
            )

        return IntegrationConfig(**data)

    def dump_schema(self, filename: str, **kwargs):
        super().dump_json(
            filename,
            "Integration config schema",
            "Schema for integration configuration file for OMTool.",
            **kwargs,
        )
