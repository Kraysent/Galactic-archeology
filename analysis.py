"""
Analysis module for OMTool. It is used for the data
analysis of existing models and the export of their parameters.
"""
import time
from typing import Callable

from amuse.lab import ScalarQuantity, units

from omtool import io_service
from omtool import json_logger as logger
from omtool import visualizer
from omtool.actions_after import VisualizerAction, fit_action, logger_action
from omtool.actions_before import slice_action
from omtool.core.analysis.config import AnalysisConfig
from omtool.core.datamodel import HandlerTask, Snapshot, profiler


def analize(config: AnalysisConfig):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    """
    actions_after: dict[str, Callable] = {}
    actions_after["logging"] = logger_action
    actions_after["fit"] = fit_action

    visualizer_service = None

    if config.visualizer is not None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        actions_after["visualizer"] = VisualizerAction(visualizer_service)

    actions_before: dict[str, Callable] = {}
    actions_before["slice"] = slice_action

    tasks = []

    for task in config.tasks:
        curr_task = HandlerTask(task.abstract_task)

        for action_params in task.actions_before:
            action_name = action_params.pop("type", None)

            if action_name is None:
                logger.error(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if action_name not in actions_before:
                logger.error(
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
                logger.error(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if handler_name not in actions_after:
                logger.error(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def handler(data, name=handler_name, params=handler_params):
                return actions_after[name](data, **params)

            curr_task.actions_after.append(handler)

        tasks.append(curr_task)

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot):
        for vtask in tasks:
            vtask.run(snapshot)

    @profiler("Saving stage")
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if visualizer_service is not None:
            visualizer_service.save({"i": iteration, "time": timestamp.value_in(units.Myr)})

    logger.info("Analysis started")

    input_service = io_service.InputService(config.input_file)
    snapshots = input_service.get_snapshot_generator()

    for (i, snapshot_tuple) in enumerate(snapshots):
        # convert iterator element to actual snapshot object
        snapshot = Snapshot(*snapshot_tuple)
        start_comp = time.time()
        loop_analysis_stage(snapshot)
        start_save = time.time()
        loop_saving_stage(i, snapshot.timestamp)
        end = time.time()

        logger.info(
            message_type="time_info",
            payload={
                "i": f"{i:03d}",
                "timestamp_Myr": f"{snapshot.timestamp.value_in(units.Myr):.01f}",
                "computation_time_s": f"{start_save - start_comp:.01f}",
                "saving_time_s": f"{end - start_save:.01f}",
            },
        )
