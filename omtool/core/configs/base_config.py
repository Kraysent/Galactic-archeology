import json
from dataclasses import dataclass

from marshmallow import EXCLUDE, Schema, fields
from marshmallow_jsonschema import JSONSchema

import omtool.json_logger as logger


@dataclass
class BaseConfig:
    logging: logger.Config


class BaseSchema(Schema):
    class Meta:
        additional_properties = True
        unknown = EXCLUDE

    logging = fields.Nested(
        logger.LoggerConfigSchema, description="This field describes logging configuration."
    )

    def dump_json(self, filename: str, title: str, description: str = "", **kwargs):
        output = JSONSchema().dump(self)
        output["title"] = title
        output["description"] = description

        with open(filename, "w") as f:
            json.dump(output, f, **kwargs)
