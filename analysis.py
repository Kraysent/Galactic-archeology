import time
from typing import Iterator, List

from amuse.lab import units

import io_service
from omtool.analysis.config import AnalysisConfig
from omtool.analysis.visual.task_manager import TaskManager
from omtool.analysis.visual.visual_task import VisualTask
from omtool.analysis.visual.visualizer import Visualizer
from omtool.datamodel import Snapshot, logger
from omtool.datamodel.task_profiler import profiler


def analize(config: AnalysisConfig):
    input_service = io_service.InputService(config.input_file)

    visualizer = Visualizer()
    task_manager = TaskManager()

    visualizer.set_figsize(*config.figsize)

    for i, plot in enumerate(config.plots):
        visualizer.add_axes(*plot.coords)
        visualizer.set_plot_parameters(i, **plot.params)

        for task in plot.tasks:
            visual_task = VisualTask(
                i, task.abstract_task, task.slice, task.display
            )

            task_manager.add_tasks(visual_task)

    number_of_snapshots = input_service.get_number_of_snapshots()
    snapshots = input_service.get_snapshot_generator()
    plot_indexes = range(number_of_snapshots)[config.plot_interval_slice]

    logger.info('i\tT, Myr\tTcomp\tTsave')

    @profiler('Analysis stage')
    def loop_analysis_stage(snapshot: Snapshot, iteration: int):
        vtask: VisualTask
        for vtask in task_manager.get_tasks():
            data = vtask.run(snapshot)

            if iteration in plot_indexes:
                visualizer.plot(vtask.axes_id, data, vtask.draw_params)

        visualizer.set_title(config.title.format(time = snapshot.timestamp.value_in(units.Myr)))

    @profiler('Saving stage')
    def loop_saving_stage(iteration: int):
        if iteration in plot_indexes:
            filename = config.pic_filename.format(i = iteration)
            visualizer.save(f'{config.output_dir}/{filename}')

    for (i, snapshot) in enumerate(snapshots):
        snapshot = Snapshot(*snapshot) # convert iterator element to actual snapshot object
        start_comp = time.time()
        loop_analysis_stage(snapshot, i)
        start_save = time.time()
        loop_saving_stage(i)
        end = time.time()

        logger.info(f'{i:03d}\t{snapshot.timestamp.value_in(units.Myr):.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
