from marshmallow import Schema, fields, post_load

from omtool.core.integrators import IntegratorConfig


class IntegratorSchema(Schema):
    name = fields.Str(required=True, description="Name of the integrator.")
    args = fields.Dict(
        fields.Str(),
        required=True,
        description="Arguments that would be passed into the constructur of the integrator.",
    )

    @post_load
    def make(self, data, **kwargs):
        return IntegratorConfig(**data)
