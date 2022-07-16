from dataclasses import dataclass

from marshmallow import Schema, fields, post_load


@dataclass
class Config:
    filename: str
    datefmt: str


class LoggerConfigSchema(Schema):
    filename = fields.Str(
        load_default="",
        description="Filename where the logs would be duplicated. If left empty, logs would be "
        "passed into stdout.",
    )
    datefmt = fields.Str(
        load_default="%Y-%m-%d %H:%M:%S", description="Simple strftime() format of the date."
    )

    @post_load
    def make(self, data: dict, **kwargs):
        return Config(**data)
