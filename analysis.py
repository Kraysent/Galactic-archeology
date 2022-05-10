"""
Analysis module for OMTool. It is used for the data
analysis of existing models and the export of their parameters.
"""
import time
from typing import Tuple

from amuse.lab import units, ScalarQuantity
import numpy as np

from omtool import visualizer
from omtool import json_logger as logger
from omtool import io_service
from omtool.core.analysis.config import AnalysisConfig
from omtool.core.analysis.visual import VisualTask
from omtool.core.datamodel import Snapshot
from omtool.core.datamodel.task_profiler import profiler


def logger_handler(data: Tuple[np.ndarray, np.ndarray], parameters: dict = None):
    """
    Handler that logs ndarrays to the INFO level.
    """
    if parameters is None:
        parameters = {}

    if parameters["print_last"]:
        logger.info(
            message_type=parameters["id"],
            payload={"x": data[0].tolist()[-1], "y": data[1].tolist()[-1]},
        )
    else:
        logger.info(
            message_type=parameters["id"],
            payload={"x": data[0].tolist(), "y": data[1].tolist()},
        )


def analize(config: AnalysisConfig):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    """
    input_service = io_service.InputService(config.input_file)

    handlers = {}
    handlers["logging"] = logger_handler

    if not config.visualizer is None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        handlers["visualizer"] = visualizer_service.plot
    else:
        visualizer_service = None

    tasks = [
        VisualTask(task.abstract_task, task.slice, task.handlers)
        for task in config.tasks
    ]

    number_of_snapshots = input_service.get_number_of_snapshots()
    plot_indexes = range(number_of_snapshots)[config.plot_interval]
    snapshots = input_service.get_snapshot_generator()

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot, iteration: int):
        vtask: VisualTask
        for vtask in tasks:
            data = vtask.run(snapshot)

            if iteration in plot_indexes:
                for key in vtask.handlers:
                    if key in handlers:
                        handlers[key](data, vtask.handlers[key])
                    else:
                        logger.error(f"{key} handler not found.")

    @profiler("Saving stage")
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if iteration in plot_indexes:
            if not visualizer_service is None:
                visualizer_service.save(
                    {"i": iteration, "time": timestamp.value_in(units.Myr)}
                )

    logger.info("Analysis started")

    for (i, snapshot) in enumerate(snapshots):
        # convert iterator element to actual snapshot object
        snapshot = Snapshot(*snapshot)
        start_comp = time.time()
        loop_analysis_stage(snapshot, i)
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
