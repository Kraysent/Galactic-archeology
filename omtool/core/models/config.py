import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Optional, Type

from amuse.lab import VectorQuantity, units
from marshmallow import Schema, fields, post_load
from zlog import logger

from omtool.core.datamodel import AbstractModel, Snapshot


@dataclass
class ModelConfig:
    name: str
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]


class ModelsSchema(Schema):
    name = fields.Str(
        required=True,
        description="Name of the model to be loaded",
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
        return ModelConfig(**data)


@dataclass
class Model:
    name: str
    model: Type


def get_model(models: list[Model], model_name: str, args: dict) -> AbstractModel | None:
    selected_models = [m.model for m in models if m.name == model_name]

    if not selected_models:
        return None

    return selected_models[0](**args)


def load_model(filename: str) -> Model:
    path = pathlib.Path(filename)

    sys.path.append(str(path.parent))
    model_module = importlib.import_module(path.stem)

    res = {
        "model": model_module.model,
        "name": model_module.model_name
        if hasattr(model_module, "model_name")
        else model_module.model.__name__,
    }

    return Model(**res)


def load_models(imports: list[str]) -> list[Model]:
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    models = []
    for filename in filenames:
        model = load_model(filename)
        models.append(model)
        logger.debug().string("name", model.name).string("from", filename).msg("imported model")

    return models


def initialize_models(imports: list[str], configs: list[ModelConfig]) -> list[Snapshot]:
    imported_models = load_models(imports)
    models: list[Snapshot] = []

    for config in configs:
        model = get_model(imported_models, config.name, config.args)

        if model is None:
            (
                logger.warn()
                .string("error", "model not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        snapshot = model.run()
        snapshot.particles.position += config.position
        snapshot.particles.velocity += config.velocity

        if config.downsample_to is not None:
            c = len(snapshot.particles) / config.downsample_to
            snapshot.particles = snapshot.particles[:: int(c)]
            snapshot.particles.mass *= c

        models.append(snapshot)
        (
            logger.info()
            .int("n", len(snapshot.particles))
            .measured_float(
                "total_mass", snapshot.particles.total_mass().value_in(units.MSun), "MSun"
            )
            .msg("added snapshot")
        )

    return models
