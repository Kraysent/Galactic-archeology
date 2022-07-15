from dataclasses import dataclass
from typing import Optional

from marshmallow import EXCLUDE, Schema, fields, post_load

from omtool import io_service, tasks, visualizer


@dataclass
class AnalysisConfig:
    input_file: io_service.Config
    visualizer: Optional[visualizer.Config]
    tasks: list[tasks.Config]


class AnalysisConfigSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    input_file = fields.Dict(fields.Str(), required=True)
    visualizer = fields.Dict(fields.Str(), load_default=None)
    tasks = fields.List(fields.Dict(fields.Str()), load_default=[])

    @post_load
    def make(self, data, **kwargs):
        if "visualizer" in data and data["visualizer"] is not None:
            data["visualizer"] = visualizer.Config.from_dict(data["visualizer"])

        if "tasks" in data:
            data["tasks"] = [tasks.Config.from_dict(task) for task in data["tasks"]]

        data["input_file"] = io_service.Config.from_dict(data["input_file"])

        return AnalysisConfig(**data)
