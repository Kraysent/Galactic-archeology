import json
from dataclasses import dataclass
from typing import Any

from marshmallow import EXCLUDE, Schema, fields
from marshmallow_jsonschema import JSONSchema


@dataclass
class BaseConfig:
    logging: dict[str, Any]


class BaseSchema(Schema):
    class Meta:
        additional_properties = True
        unknown = EXCLUDE

    logging = fields.Dict(fields.Str, description="This field describes logging configuration.")

    def dump_json(self, filename: str, title: str, description: str = "", **kwargs):
        output = JSONSchema().dump(self)
        output["title"] = title
        output["description"] = description

        with open(filename, "w") as f:
            json.dump(output, f, **kwargs)
