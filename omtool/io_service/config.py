from dataclasses import dataclass
from typing import List

from marshmallow import Schema, fields, post_load


@dataclass
class Config:
    format: str
    filenames: List[str]


class IOConfigSchema(Schema):
    format = fields.Str(required=True)
    filenames = fields.List(fields.Str(), required=True)

    @post_load
    def make(self, data: dict, **kwargs):
        return Config(**data)
