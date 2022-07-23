"""
Analysis module for OMTool. It is used for the data
analysis of existing models and the export of their parameters.
"""
import time
from typing import Callable

from amuse.lab import ScalarQuantity, units
from zlog import logger

from omtool import io_service, visualizer
from omtool.actions_after import initialize_actions_after
from omtool.actions_before import initialize_actions_before
from omtool.core.configs import AnalysisConfig
from omtool.core.datamodel import Snapshot, profiler
from omtool.core.utils import initialize_logger
from omtool.tasks import initialize_tasks


def analize(config: AnalysisConfig):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    """
    initialize_logger(**config.logging)
    visualizer_service = (
        visualizer.VisualizerService(config.visualizer) if config.visualizer is not None else None
    )
    actions_after: dict[str, Callable] = initialize_actions_after(visualizer_service)
    actions_before = initialize_actions_before()
    tasks = initialize_tasks(config.tasks, actions_before, actions_after)

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot):
        for vtask in tasks:
            vtask.run(snapshot)

    @profiler("Saving stage")
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if visualizer_service is not None:
            visualizer_service.save({"i": iteration, "time": timestamp.value_in(units.Myr)})

    logger.info().msg("Analysis started")

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

        (
            logger.info()
            .string("id", "time_data")
            .int("i", i)
            .float("timestamp_Myr", snapshot.timestamp.value_in(units.Myr))
            .float("computation_time_s", start_save - start_comp)
            .float("saving_time_s", end - start_save)
            .send()
        )
