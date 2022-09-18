from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from amuse.lab import VectorQuantity, units
from scipy.spatial.transform import Rotation
from zlog import logger

from omtool.core.models.abstract_model import AbstractModel, Snapshot
from omtool.core.models.plugin import MODELS
from omtool.core.utils import import_modules


@dataclass
class RotationConfig:
    axis: str
    angle: float


@dataclass
class ModelConfig:
    name: str
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]
    rotation: RotationConfig


def get_model(model_name: str, args: dict) -> AbstractModel | None:
    return MODELS[model_name](**args) if model_name in MODELS else None


def add_offset(model: Snapshot, pos_offset: VectorQuantity, vel_offset: VectorQuantity) -> Snapshot:
    model.particles.position += pos_offset
    model.particles.velocity += vel_offset
    return model


def downsample(model: Snapshot, target_number: int) -> Snapshot:
    c = len(model.particles) / target_number
    subset_indices = np.random.choice(len(model.particles), target_number, replace=False)
    model.particles = model.particles[subset_indices]
    model.particles.mass *= c

    return model


def rotate(model: Snapshot, axis: str, angle: float) -> Snapshot:
    if axis == "x":
        vec = np.array([1, 0, 0])
    elif axis == "y":
        vec = np.array([0, 1, 0])
    elif axis == "z":
        vec = np.array([0, 0, 1])
    else:
        raise ValueError("Unknown axis specified in rotation parameters.")

    rot_matrix = Rotation.from_rotvec(angle * vec).as_matrix()

    cm = model.particles.center_of_mass()
    cm_vel = model.particles.center_of_mass_velocity()
    model.particles.position -= cm
    model.particles.velocity -= cm_vel

    model.particles.position = np.dot(model.particles.position, rot_matrix.T)
    model.particles.velocity = np.dot(model.particles.velocity, rot_matrix.T)

    model.particles.position += cm
    model.particles.velocity += cm_vel

    return model


def initialize_models(imports: list[str], configs: list[ModelConfig]) -> list[Snapshot]:
    import_modules(imports)
    models: list[Snapshot] = []

    for config in configs:
        model = get_model(config.name, config.args)

        if model is None:
            (
                logger.warn()
                .string("error", "model not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        snapshot = model.run()
        snapshot = add_offset(snapshot, config.position, config.velocity)
        logger.debug().msg("added offset")

        if config.downsample_to is not None:
            n = len(snapshot.particles)
            snapshot = downsample(snapshot, config.downsample_to)
            logger.debug().int("from", n).int("to", len(snapshot.particles)).msg("downsampled")

        if config.rotation is not None:
            snapshot = rotate(snapshot, config.rotation.axis, config.rotation.angle)
            (
                logger.debug()
                .string("around", config.rotation.axis)
                .int("angle", config.rotation.angle)
                .msg("rotated")
            )

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
