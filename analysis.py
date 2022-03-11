import time

from amuse.lab import units, ScalarQuantity

import io_service
import logger
from omtool.analysis.config import AnalysisConfig
from omtool.analysis.visual.task_manager import TaskManager
from omtool.analysis.visual.visual_task import VisualTask
from omtool.datamodel import Snapshot
from omtool.datamodel.task_profiler import profiler
import visualizer


def analize(config: AnalysisConfig):
    input_service = io_service.InputService(config.input_file)
    visualizer_service = visualizer.VisualizerService(config.visualizer)

    handlers = {
        "visualizer": visualizer_service.run_handler
    }

    task_manager = TaskManager()

    for i, task in enumerate(config.tasks):
        visual_task = VisualTask(
            i, task.abstract_task, task.slice, task.handlers
        )

        task_manager.add_tasks(visual_task)

    number_of_snapshots = input_service.get_number_of_snapshots()
    plot_indexes = range(number_of_snapshots)[config.plot_interval]
    snapshots = input_service.get_snapshot_generator()

    logger.info('i\tT, Myr\tTcomp\tTsave')

    @profiler('Analysis stage')
    def loop_analysis_stage(snapshot: Snapshot, iteration: int):
        vtask: VisualTask
        for vtask in task_manager.get_tasks():
            data = vtask.run(snapshot)

            if iteration in plot_indexes:
                for key in vtask.handlers:
                    if key in handlers:
                        handlers[key](data, vtask.handlers[key])

    @profiler('Saving stage')
    def loop_saving_stage(iteration: int, time: ScalarQuantity):
        if iteration in plot_indexes:
            visualizer_service.save({"i": iteration, "time": time.value_in(units.Myr)})

    for (i, snapshot) in enumerate(snapshots):
        snapshot = Snapshot(*snapshot) # convert iterator element to actual snapshot object
        start_comp = time.time()
        loop_analysis_stage(snapshot, i)
        start_save = time.time()
        loop_saving_stage(i, snapshot.timestamp)
        end = time.time()

        logger.info(f'{i:03d}\t{snapshot.timestamp.value_in(units.Myr):.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
