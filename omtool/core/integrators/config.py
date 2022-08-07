from dataclasses import dataclass
from typing import Any

from zlog import logger

from omtool.core.datamodel import AbstractIntegrator
from omtool.core.integrators.plugin import INTEGRATORS
from omtool.core.utils import import_modules


@dataclass
class IntegratorConfig:
    name: str
    args: dict[str, Any]


def get_integrator(integrator_name: str, args: dict) -> AbstractIntegrator | None:
    return INTEGRATORS[integrator_name](**args) if integrator_name in INTEGRATORS else None


def initialize_integrator(imports: list[str], config: IntegratorConfig) -> AbstractIntegrator:
    import_modules(imports)

    integrator = get_integrator(config.name, config.args)
    if integrator is None:
        logger.error().string("name", config.name).msg("integrator not found")
        raise ImportError(f"integrator {config.name} not found")

    logger.debug().string("name", config.name).msg("loaded integrator")
    return integrator
