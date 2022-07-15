from dataclasses import dataclass

from marshmallow import Schema, fields, post_load


@dataclass
class Config:
    filename: str
    datefmt: str


class LoggerConfigSchema(Schema):
    filename = fields.Str()
    datefmt = fields.Str()

    @post_load
    def make(self, data: dict, **kwargs):
        return Config(**data)
