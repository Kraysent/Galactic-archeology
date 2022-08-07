from amuse.lab import VectorQuantity, units
from marshmallow import Schema, fields, post_load

from omtool.core.models import ModelConfig


class ModelSchema(Schema):
    name = fields.Str(
        required=True,
        description="Name of the model to be loaded",
    )
    args = fields.Dict(
        fields.Str(),
        description="Arguments that would be passed to to constructor of a given model.",
    )
    position = fields.Raw(
        load_default=VectorQuantity([0, 0, 0], units.kpc),
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
        return ModelConfig(**data)
