from marshmallow import fields, post_load

from cli.python_schemas.base_schema import BaseSchema
from cli.python_schemas.tasks_schema import TaskConfigSchema
from omtool import io_service, visualizer
from omtool.core.configs import AnalysisConfig


class AnalysisConfigSchema(BaseSchema):
    input_file = fields.Nested(
        io_service.IOConfigSchema,
        required=True,
        description="Parameters of input file: its format and path.",
    )
    visualizer = fields.Nested(
        visualizer.VisualizerConfigSchema,
        load_default=None,
        description="Visualizer is responsible for the matplotlib's plots, their layout and format "
        "of the data. This fields describes layout; format of the data is specified inside tasks.",
    )
    tasks = fields.List(
        fields.Nested(TaskConfigSchema),
        load_default=[],
        description="This field describes list of tasks. Each task is a class that has run(...) "
        "method that processes Snapshot and returns some data.",
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return AnalysisConfig(**data)

    def dump_schema(self, filename: str, **kwargs):
        super().dump_json(
            filename,
            "Analysis config schema",
            "Schema for analysis configuration file for OMTool.",
            **kwargs
        )
