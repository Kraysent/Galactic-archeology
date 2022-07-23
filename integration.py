"""
Integration module for OMTool. Used to integrate existing model
from the file and write it to another file.
"""
import os
from pathlib import Path
from typing import Callable

from amuse.lab import units
from zlog import logger

from omtool import io_service, visualizer
from omtool.actions_after import initialize_actions_after
from omtool.actions_before import initialize_actions_before
from omtool.core.configs import IntegrationConfig
from omtool.core.datamodel import Snapshot, profiler
from omtool.core.integrators import get_integrator
from omtool.core.utils import initialize_logger
from omtool.tasks import initialize_tasks


def integrate(config: IntegrationConfig):
    """
    Integration mode for the OMTool. Used to integrate existing model
    from the file and write it to another file.
    """
    initialize_logger(**config.logging)
    visualizer_service = (
        visualizer.VisualizerService(config.visualizer) if config.visualizer is not None else None
    )
    actions_after: dict[str, Callable] = initialize_actions_after(visualizer_service)
    actions_before = initialize_actions_before()
    tasks = initialize_tasks(config.tasks, actions_before, actions_after)

    # TODO: move this logic to config schemas
    if config.overwrite:
        if Path(config.output_file).is_file():
            os.remove(config.output_file)
    else:
        if Path(config.output_file).is_file():
            raise Exception(
                f'Output file ({config.output_file}) exists and "overwrite" '
                "option in integration config file is false (default)"
            )

    input_service = io_service.InputService(config.input_file)
    integrator = get_integrator(
        config.integrator.name,
        Snapshot(*next(input_service.get_snapshot_generator())),
        config.integrator.args,
    )

    @profiler("Integration stage")
    def loop_integration_stage() -> Snapshot:
        integrator.leapfrog()

        return integrator.get_snapshot()

    @profiler("Analysis stage")
    def loop_analysis_stage(iteration: int, snapshot: Snapshot):
        for vtask in tasks:
            vtask.run(snapshot)

        if visualizer_service is not None:
            visualizer_service.save(
                {"i": iteration, "time": snapshot.timestamp.value_in(units.Myr)}
            )

    @profiler("Saving to file stage")
    def loop_saving_stage(iteration: int, snapshot: Snapshot):
        if iteration % config.snapshot_interval == 0:
            snapshot.to_fits(config.output_file, append=True)

        for log in config.logs:
            particle = integrator.get_particle(log.point_id)
            (
                logger.info()
                .string("id", log.logger_id)
                .float("timestamp", integrator.timestamp.value_in(units.Myr))
                .float("x", particle.x.value_in(units.kpc))
                .float("y", particle.y.value_in(units.kpc))
                .float("z", particle.z.value_in(units.kpc))
                .float("vx", particle.vx.value_in(units.kms))
                .float("vy", particle.vy.value_in(units.kms))
                .float("vz", particle.vz.value_in(units.kms))
            ).send()

        logger.info().string("id", "integration_timing").float(
            "timestamp", integrator.timestamp.value_in(units.Myr)
        ).send()

    logger.info().msg("Integration started")
    i = 0

    while integrator.timestamp < config.model_time:
        snapshot = loop_integration_stage()
        loop_analysis_stage(i, snapshot)
        loop_saving_stage(i, snapshot)

        i += 1
