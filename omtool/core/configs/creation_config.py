from dataclasses import dataclass
from pathlib import Path

from marshmallow import fields, post_load

from omtool.core.configs.base_config import BaseConfig, BaseSchema
from omtool.core.models import ModelConfig, ModelsSchema


@dataclass
class CreationConfig(BaseConfig):
    output_file: str
    overwrite: bool
    objects: list[ModelConfig]


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
        ModelsSchema,
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
