from marshmallow import Schema, fields, post_load

from omtool.core.tasks import TasksConfig


class TaskConfigSchema(Schema):
    name = fields.Raw(required=True, description="Name of the task.")
    actions_before = fields.List(
        fields.Dict(fields.Str()),
        load_default=[],
        description="List of actions that would run some function on a given snapshot "
        "before running the task.",
    )
    actions_after = fields.List(
        fields.Dict(fields.Str()),
        load_default=[],
        description="List of actions that would run some function on every single result "
        "of the task.",
    )
    args = fields.Dict(
        fields.Str(), load_default={}, description="Arguments to the constructor of the task."
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return TasksConfig(**data)
