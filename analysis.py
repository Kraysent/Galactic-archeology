import atexit
import logging
import time
from typing import Iterator, List

from amuse.lab import units
from omtool.analysis.config import AnalysisConfig

from omtool.analysis.visual.task_manager import TaskManager
from omtool.analysis.visual.visual_task import VisualTask
from omtool.analysis.visual.visualizer import Visualizer
from omtool.datamodel import Snapshot
from omtool.datamodel.task_profiler import ProfilerSingleton

def generate_snapshot(fmt: str, files: List[str]) -> Iterator[Snapshot]:
    if fmt == 'fits':
        return Snapshot.from_fits(files[0])
    elif fmt == 'csv':
        return Snapshot.from_logged_csvs(files, delimiter = ' ')

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

    plot_interval = config.plot_interval

    @atexit.register
    def print_times():
        profiler_instance = ProfilerSingleton.get_instance()
        res = profiler_instance.dump_times()

        for key, val in res.items():
            logging.info(f'{key} worked {val:.02f} seconds on average')

    logging.info('i\tT, Myr\tTcomp\tTsave')

    for (i, snapshot) in enumerate(snapshots):
        start_comp = time.time()

        vtask: VisualTask
        for vtask in task_manager.get_tasks():
            data = vtask.run(snapshot)

            if i % plot_interval == 0:
                visualizer.plot(vtask.axes_id, data, vtask.draw_params)

        timestamp = snapshot.timestamp.value_in(units.Myr)
        visualizer.set_title(f'Time: {timestamp:.02f} Myr')

        start_save = time.time()

        if i % plot_interval == 0:
            visualizer.save(f'{config.output_dir}/img-{i:03d}.png')

        end = time.time()
        logging.info(f'{i:03d}\t{timestamp:.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
