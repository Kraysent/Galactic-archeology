"""
Analysis module for OMTool. It is used for the data
analysis of existing models and the export of their parameters.
"""
import time

from amuse.lab import units, ScalarQuantity

from omtool import visualizer
from omtool import json_logger as logger
from omtool import io_service
from omtool.core.analysis.config import AnalysisConfig
from omtool.core.analysis.visual import VisualTask
from omtool.core.datamodel import Snapshot
from omtool.core.datamodel.task_profiler import profiler
from omtool.handlers import logger_handler


def analize(config: AnalysisConfig):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    """
    input_service = io_service.InputService(config.input_file)

    handlers = {}
    handlers["logging"] = logger_handler

    visualizer_service = None

    if not config.visualizer is None:
        visualizer_service = visualizer.VisualizerService(config.visualizer)
        handlers["visualizer"] = visualizer_service.plot

    tasks = [
        VisualTask(
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

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot):
        for vtask in tasks:
            vtask.run(snapshot)

    @profiler("Saving stage")
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if not visualizer_service is None:
            visualizer_service.save(
                {"i": iteration, "time": timestamp.value_in(units.Myr)}
            )

    logger.info("Analysis started")

    snapshots = input_service.get_snapshot_generator()

    for (i, snapshot) in enumerate(snapshots):
        # convert iterator element to actual snapshot object
        snapshot = Snapshot(*snapshot)
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
