import json

from marshmallow import EXCLUDE, Schema, fields, post_load
from marshmallow_jsonschema import JSONSchema

from omtool.core.configs import ImportsConfig


class ImportsSchema(Schema):
    tasks = fields.List(
        fields.Str,
        description="This field lists tasks that would be used in this simulation.",
        load_default=["tools/tasks/*"],
    )
    models = fields.List(
        fields.Str,
        description="This field lists models that would be used to create snapshot.",
        load_default=["tools/models/*"],
    )
    integrators = fields.List(
        fields.Str,
        description="This field lists integrators that would be used to model snapshot.",
        load_default=["tools/integrators/*"],
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return ImportsConfig(**data)


class BaseSchema(Schema):
    class Meta:
        additional_properties = True
        unknown = EXCLUDE

    logging = fields.Dict(
        fields.Str, description="This field describes logging configuration.", load_default={}
    )
    imports = fields.Nested(
        ImportsSchema,
        description="This field lists imports for various actions.",
        load_default=ImportsConfig(["tools/tasks/*"], ["tools/models/*"], ["tools/integrators/*"]),
    )

    def dump_json(self, filename: str, title: str, description: str = "", **kwargs):
        output = JSONSchema().dump(self)
        output["title"] = title
        output["description"] = description

        with open(filename, "w") as f:
            json.dump(output, f, **kwargs)
