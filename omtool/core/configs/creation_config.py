from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from amuse.lab import VectorQuantity, units
from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

import omtool.json_logger as logger


class Type(Enum):
    BODY = "body"
    CSV = "csv"
    PLUMMER_SPHERE = "plummer_sphere"


@dataclass
class Object:
    type: Type
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]


@dataclass
class CreationConfig:
    output_file: str
    overwrite: bool
    logging: logger.Config
    objects: list[Object]


class ObjectsSchema(Schema):
    type = EnumField(Type, by_value=True, required=True)
    args = fields.Dict(fields.Str())
    position = fields.Raw(load_default=VectorQuantity([0, 0, 0], units.kms))
    velocity = fields.Raw(load_default=VectorQuantity([0, 0, 0], units.kms))
    downsample_to = fields.Int(load_default=None)

    @post_load
    def make(self, data: dict, **kwargs):
        return Object(**data)


class CreationConfigSchema(Schema):
    output_file = fields.Str(required=True)
    overwrite = fields.Bool(load_default=False)
    logging = fields.Nested(logger.LoggerConfigSchema)
    objects = fields.Nested(ObjectsSchema, many=True, required=True)

    @post_load
    def make(self, data: dict, **kwargs):
        return CreationConfig(**data)
