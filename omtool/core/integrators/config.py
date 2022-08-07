import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Any

from zlog import logger

from omtool.core.datamodel import AbstractIntegrator
from omtool.core.integrators.plugin import INTEGRATORS


@dataclass
class IntegratorConfig:
    name: str
    args: dict[str, Any]


def get_integrator(integrator_name: str, args: dict) -> AbstractIntegrator | None:
    return INTEGRATORS[integrator_name](**args) if integrator_name in INTEGRATORS else None


def import_integrators(imports: list[str]):
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    for filename in filenames:
        path = pathlib.Path(filename)
        sys.path.append(str(path.parent))
        importlib.import_module(path.stem)


def initialize_integrator(imports: list[str], config: IntegratorConfig) -> AbstractIntegrator:
    import_integrators(imports)

    integrator = get_integrator(config.name, config.args)
    if integrator is None:
        logger.error().string("name", config.name).msg("integrator not found")
        raise ImportError(f"integrator {config.name} not found")

    logger.debug().string("name", config.name).msg("loaded integrator")
    return integrator
