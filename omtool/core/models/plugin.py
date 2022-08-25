from typing import Type

from zlog import logger

from omtool.core.models.abstract_model import AbstractModel

MODELS = {}


def register_model(name: str):
    if name in MODELS:
        logger.error().string("name", name).msg("name conflict when importing model")
        return

    def wrapper_register_model(model_class: Type[AbstractModel]):
        logger.debug().string("name", name).msg("imported model")
        MODELS[name] = model_class
        return model_class

    return wrapper_register_model
