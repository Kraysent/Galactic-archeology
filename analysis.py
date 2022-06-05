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
from omtool.core.analysis.config import AnalysisConfig
from omtool.core.datamodel import HandlerTask, Snapshot, profiler
from omtool.handlers import logger_handler


def analize(config: AnalysisConfig):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    """
    input_service = io_service.InputService(config.input_file)

    handlers: dict[str, Callable] = {}
    handlers["logging"] = logger_handler

    visualizer_service = None

    if config.visualizer is not None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        handlers["visualizer"] = visualizer_service.plot

    tasks = []

    for task in config.tasks:
        curr_task = HandlerTask(task.abstract_task, task.slice)

        for handler_params in task.handlers:
            handler_name = handler_params.pop("type", None)

            if handler_name is None:
                logger.error(f"Handler type {handler_name} of the task {type(curr_task.task)} is not specified, skipping.")
                continue

            if handler_name not in handlers:
                logger.error(f"Handler type {handler_name} of the task {type(curr_task.task)} is unknown, skipping.")
                continue

            def handler(data, name=handler_name, params=handler_params):
                return handlers[name](data, params)

            curr_task.handlers.append(handler)

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
