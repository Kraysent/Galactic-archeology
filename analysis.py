'''
Analysis module for OMTool. It is used for the data
analysis of existing models and the export of their parameters.
'''
import time
from typing import Tuple

from amuse.lab import units, ScalarQuantity
import numpy as np

import io_service
import json_logger as logger
from omtool.analysis.config import AnalysisConfig
from omtool.analysis.visual.task_manager import TaskManager
from omtool.analysis.visual.visual_task import VisualTask
from omtool.datamodel import Snapshot
from omtool.datamodel.task_profiler import profiler
import visualizer


def logger_handler(data: Tuple[np.ndarray, np.ndarray], parameters: dict = None):
    '''
    Handler that logs ndarrays to the INFO level.
    '''
    if parameters is None:
        parameters = {}

    if parameters['print_last']:
        logger.info(f'x: {data[0].tolist()[-1]}, y: {data[1].tolist()[-1]}')
    else:
        logger.info(f'x: {data[0].tolist()}, y: {data[1].tolist()}')


def analize(config: AnalysisConfig):
    '''
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
    '''
    input_service = io_service.InputService(config.input_file)
    visualizer_service = visualizer.VisualizerService(config.visualizer)

    handlers = {
        'visualizer': visualizer_service.plot,
        'logging': logger_handler
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
                    else:
                        logger.error(f'{key} handler not found.')

    @profiler('Saving stage')
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if iteration in plot_indexes:
            visualizer_service.save(
                {"i": iteration, "time": timestamp.value_in(units.Myr)})

    for (i, snapshot) in enumerate(snapshots):
        # convert iterator element to actual snapshot object
        snapshot = Snapshot(*snapshot)
        start_comp = time.time()
        loop_analysis_stage(snapshot, i)
        start_save = time.time()
        loop_saving_stage(i, snapshot.timestamp)
        end = time.time()

        logger.info(
            f'{i:03d}\t{snapshot.timestamp.value_in(units.Myr):.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
