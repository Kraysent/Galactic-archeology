"""
Integration module for OMTool. Used to integrate existing model
from the file and write it to another file.
"""
import os
from pathlib import Path
from typing import Callable, Dict

from amuse.lab import units
from zlog import logger

from omtool import io_service, visualizer
from omtool.actions_after import VisualizerAction, logger_action
from omtool.core.configs import IntegrationConfig
from omtool.core.datamodel import HandlerTask, Snapshot, profiler
from omtool.core.integrators import get_integrator
from omtool.core.utils import initialize_logger


def integrate(config: IntegrationConfig):
    """
    Integration mode for the OMTool. Used to integrate existing model
    from the file and write it to another file.
    """
    initialize_logger(**config.logging)
    actions_after: Dict[str, Callable] = {}
    actions_after["logging"] = logger_action

    visualizer_service = None

    if config.visualizer is not None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        actions_after["visualizer"] = VisualizerAction(visualizer_service)

    actions_before: Dict[str, Callable] = {}
    actions_before["slice"] = lambda snapshot, part: snapshot[slice(*part)]

    tasks = []

    for task in config.tasks:
        curr_task = HandlerTask(task.name)

        for action_params in task.actions_before:
            action_name = action_params.pop("type", None)

            if action_name is None:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if action_name not in actions_before:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def action(snapshot, name=action_name, params=action_params):
                return actions_before[name](snapshot, **params)

            curr_task.actions_before.append(action)

        for handler_params in task.actions_after:
            handler_name = handler_params.pop("type", None)

            if handler_name is None:
                logger.error().msg(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if handler_name not in actions_after:
                logger.error().msg(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def handler(data, name=handler_name, params=handler_params):
                return actions_after[name](data, **params)

            curr_task.actions_after.append(handler)

        tasks.append(curr_task)

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
                .float("vx", particle.vx.value_in(units.kpc))
                .float("vy", particle.vy.value_in(units.kpc))
                .float("vz", particle.vz.value_in(units.kpc))
            )

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
