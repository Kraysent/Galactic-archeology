from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from amuse.lab import VectorQuantity, units
from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from omtool.core.configs.base_config import BaseConfig, BaseSchema


class Type(Enum):
    body = 1
    csv = 2
    plummer_sphere = 3


@dataclass
class Object:
    type: Type
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]


@dataclass
class CreationConfig(BaseConfig):
    output_file: str
    overwrite: bool
    objects: list[Object]


class ObjectsSchema(Schema):
    type = EnumField(
        Type,
        required=True,
        description="""
        Type of object to be created. Can either be 'csv', 'body' or 'plummer_sphere'.

        csv - model listed in *.csv file with following format: 'x,y,z,vx,vy,vz,m'.
        body - actual particles described by its mass.
        plummer_sphere - model with given number of particles and mass described
        by the Plummer model.
        """,
    )
    args = fields.Dict(
        fields.Str(),
        description="Arguments that would be passed to to constructor of a given model.",
    )
    position = fields.Raw(
        load_default=VectorQuantity([0, 0, 0], units.kms),
        type="array",
        description="Initial offset of the whole model. If there is more than one particle, "
        "it would be applied to each particle.",
    )
    velocity = fields.Raw(
        load_default=VectorQuantity([0, 0, 0], units.kms),
        type="array",
        description="Initial velocity of the whole model. If there is more than one particle, "
        "it would be applied to each particle.",
    )
    downsample_to = fields.Int(
        load_default=None,
        description="Target length of downsampling. If one does not need all the particles from "
        "the model, they may decrease it to this number and increase the mass correspondingly.",
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return Object(**data)


class CreationConfigSchema(BaseSchema):
    output_file = fields.Str(
        required=True, description="Path to file where output model would be saved."
    )
    overwrite = fields.Bool(
        load_default=False,
        description="Flag that shows whether to overwrite model if it "
        "already exists on given filepath.",
    )
    objects = fields.Nested(
        ObjectsSchema,
        many=True,
        required=True,
        description="This field list of objects. Each object is either a body or a model. Models "
        "can be loaded from *.csv in specific format or generated based on some function.",
    )

    @post_load
    def make(self, data: dict, **kwargs):
        if not data["overwrite"] and Path(data["output_file"]).is_file():
            raise FileExistsError(
                f'Output file ({data["output_file"]}) exists and "overwrite" '
                "option in integration config file is false (default)"
            )
        return CreationConfig(**data)

    def dump_schema(self, filename: str, **kwargs):
        super().dump_json(
            filename,
            "Creation config schema",
            "Schema for creation configuration file for OMTool.",
            **kwargs,
        )
