import logging
import time
from typing import Iterator, List

from amuse.lab import units
from omtool.analysis.config import AnalysisConfig

from omtool.analysis.visual.task_manager import TaskManager
from omtool.analysis.visual.visual_task import VisualTask
from omtool.analysis.visual.visualizer import Visualizer
from omtool.datamodel import Snapshot
from omtool.datamodel.task_profiler import profiler

def generate_snapshot(fmt: str, files: List[str]) -> Iterator[Snapshot]:
    if fmt == 'fits':
        return Snapshot.from_fits(files[0])
    elif fmt == 'csv':
        return Snapshot.from_logged_csvs(files, delimiter = ' ')

@profiler('Analysis stage')
def loop_analysis_stage(
    visualizer: Visualizer, 
    task_manager: TaskManager, 
    snapshot: Snapshot, 
    iteration: int,
    config: AnalysisConfig
):
    vtask: VisualTask
    for vtask in task_manager.get_tasks():
        data = vtask.run(snapshot)

        if iteration % config.plot_interval == 0:
            visualizer.plot(vtask.axes_id, data, vtask.draw_params)

    visualizer.set_title(config.title.format(time = snapshot.timestamp.value_in(units.Myr)))

@profiler('Saving stage')
def loop_saving_stage(
    visualizer: Visualizer, 
    iteration: int, 
    config: AnalysisConfig
):
    if iteration % config.plot_interval == 0:
        visualizer.save(f'{config.output_dir}/img-{iteration:03d}.png')

def analize(config: AnalysisConfig):
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

    snapshots = generate_snapshot(config.input_file.format, config.input_file.filenames)

    logging.info('i\tT, Myr\tTcomp\tTsave')

    for (i, snapshot) in enumerate(snapshots):
        start_comp = time.time()
        loop_analysis_stage(visualizer, task_manager, snapshot, i, config)
        start_save = time.time()
        loop_saving_stage(visualizer, i, config)
        end = time.time()

        logging.info(f'{i:03d}\t{snapshot.timestamp.value_in(units.Myr):.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
