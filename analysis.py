import logging
import time
from typing import Iterator, Union

from amuse.lab import units
from archeology.analysis.tasks.abstract_task import get_task
from archeology.analysis.visual.plot_parameters import DrawParameters

from archeology.analysis.visual.task_manager import TaskManager
from archeology.analysis.visual.visual_task import VisualTask
from archeology.analysis.visual.visualizer import Visualizer
from archeology.datamodel import Config, Snapshot

def generate_snapshot(fmt: str, files: list[str]) -> Iterator[Snapshot]:
    if fmt == 'fits':
        return Snapshot.from_fits(files[0])
    elif fmt == 'csv':
        return Snapshot.from_logged_csvs(files, delimiter = ' ')

def analize(config: Config):
    visualizer = Visualizer()
    task_manager = TaskManager()

    visualizer.set_figsize(*config['figsize'])

    for i, plot in enumerate(config['plots']):
        visualizer.add_axes(*plot['coords'])
        visualizer.set_plot_parameters(i, **plot['params'])

        if 'tasks' in plot:
            for task in plot['tasks']:
                abstract_task = get_task(task['name'], task['args'])
                
                if 'slice' in task:
                    curr_slice = task['slice']
                    curr_slice = slice(curr_slice[0], curr_slice[1])
                else: 
                    curr_slice = slice(0, None)

                visual_task = VisualTask(
                    i, abstract_task, curr_slice, DrawParameters(**task['display'])
                )

                task_manager.add_tasks(visual_task)

    snapshots = generate_snapshot(config['input_file']['format'], config['input_file']['filenames'])

    logging.info('i\tT, Myr\tTcomp\tTsave')

    for (i, snapshot) in enumerate(snapshots):
        start_comp = time.time()

        vtask: VisualTask
        for vtask in task_manager.get_tasks():
            data = vtask.run(snapshot)
            visualizer.plot(vtask.axes_id, data, vtask.draw_params)

        timestamp = snapshot.timestamp.value_in(units.Myr)
        visualizer.set_title(f'Time: {timestamp:.02f} Myr')

        start_save = time.time()
        visualizer.save(f'{config["output_dir"]}/img-{i:03d}.png')

        end = time.time()
        logging.info(f'{i:03d}\t{timestamp:.01f}\t{start_save - start_comp:.01f}\t{end - start_save:.01f}')
