"""
Module that describes all of the integrators.
"""
from omtool.core.datamodel import Snapshot
from omtool.core.integration.integrators.pyfalcon_integrator import PyfalconIntegrator


def get_integrator(integrator_name: str, snapshot: Snapshot, args: dict):
    """
    Creates instance of a specific integrator with arguments that were provided in args dict.
    """
    integrators_map = {"pyfalcon": PyfalconIntegrator}

    return integrators_map[integrator_name](snapshot, **args)
