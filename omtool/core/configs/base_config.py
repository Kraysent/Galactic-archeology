from dataclasses import dataclass

from marshmallow import EXCLUDE, Schema, fields

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
