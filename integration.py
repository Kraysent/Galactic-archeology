"""
Integration module for OMTool. Used to integrate existing model
from the file and write it to another file.
"""
import os
from pathlib import Path

from amuse.lab import units

from omtool import io_service, visualizer
from omtool import json_logger as logger
from omtool.core.datamodel import HandlerTask, Snapshot, profiler
from omtool.core.integration.integrators import get_integrator
from omtool.core.integration.config import IntegrationConfig
from omtool.handlers import logger_handler


def integrate(config: IntegrationConfig):
    """
    Integration mode for the OMTool. Used to integrate existing model
    from the file and write it to another file.
    """
    input_service = io_service.InputService(config.input_file)
    integrator = get_integrator(
        config.integrator.name,
        Snapshot(*next(input_service.get_snapshot_generator())),
        config.integrator.args,
    )

    handlers = {}
    handlers["logging"] = logger_handler

    visualizer_service = None

    if not config.visualizer is None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        handlers["visualizer"] = visualizer_service.plot

    tasks = [
        HandlerTask(
            task.abstract_task,
            task.slice,
            [
                lambda data, key=key, handler_params=value: handlers[key](
                    data, handler_params
                )
                for key, value in task.handlers.items()
            ],
        )
        for task in config.tasks
    ]

    if config.overwrite:
        if Path(config.output_file).is_file():
            os.remove(config.output_file)
    else:
        if Path(config.output_file).is_file():
            raise Exception(
                f'Output file ({config.output_file}) exists and "overwrite" option in integration config file is false (default)'
            )

    @profiler("Integration stage")
    def loop_integration_stage() -> Snapshot:
        integrator.leapfrog()

        return integrator.get_snapshot()

    @profiler("Analysis stage")
    def loop_analysis_stage(iteration: int, snapshot: Snapshot):
        for vtask in tasks:
            vtask.run(snapshot)

        if not visualizer_service is None:
            visualizer_service.save(
                {"i": iteration, "time": snapshot.timestamp.value_in(units.Myr)}
            )

    @profiler("Saving to file stage")
    def loop_saving_stage(iteration: int, snapshot: Snapshot):
        if iteration % config.snapshot_interval == 0:
            snapshot.to_fits(config.output_file, append=True)

        for log in config.logs:
            particle = integrator.get_particle(log.point_id)
            logger.info(
                message_type=log.logger_id,
                payload={
                    "timestamp": integrator.timestamp.value_in(units.Myr),
                    "x": particle.x.value_in(units.kpc),
                    "y": particle.y.value_in(units.kpc),
                    "z": particle.z.value_in(units.kpc),
                    "vx": particle.vx.value_in(units.kms),
                    "vy": particle.vy.value_in(units.kms),
                    "vz": particle.vz.value_in(units.kms),
                    "m": particle.mass.value_in(units.MSun),
                },
            )

        logger.info(
            message_type="integration_timing",
            payload={"timestamp": integrator.timestamp.value_in(units.Myr)},
        )

    logger.info("Integration started")
    i = 0

    while integrator.timestamp < config.model_time:
        snapshot = loop_integration_stage()
        loop_analysis_stage(i, snapshot)
        loop_saving_stage(i, snapshot)

        i += 1
