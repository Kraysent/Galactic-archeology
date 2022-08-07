from typing import Type

from zlog import logger

from omtool.core.datamodel import AbstractIntegrator

INTEGRATORS = {}


def register_integrator(name: str):
    if name in INTEGRATORS:
        logger.error().string("name", name).msg("name conflict when importing model")
        return

    def wrapper_register_integrator(integrator_class: Type[AbstractIntegrator]):
        logger.debug().string("name", name).msg("imported integrator")
        INTEGRATORS[name] = integrator_class
        return integrator_class

    return wrapper_register_integrator
