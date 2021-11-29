import logging
import time

from amuse.lab import units
from archeology.analysis.visual.nbody_object import NbodyObject

from archeology.analysis.visual.task_manager import TaskManager
from archeology.analysis.visual.visual_task import VisualTask
from archeology.analysis.visual.visualizer import Visualizer
from archeology.datamodel import Config, Snapshot


def analize(config: Config):
    visualizer = Visualizer()

    for i, plot in enumerate(config['plots']):
        visualizer.add_axes(*plot['coords'])
        visualizer.set_plot_parameters(i, **plot['params'])

    visualizer.set_figsize(*config['figsize'])

    objects = []

    for curr_obj in config['objects']:
        curr_slice = curr_obj['slice']
        curr_slice = slice(curr_slice[0], curr_slice[1])

        obj = NbodyObject(curr_obj['color'], curr_obj['name'], curr_slice)
        objects.append(obj)

    task_manager = TaskManager(objects)

    task_manager.add_left_spatial_tasks()
    task_manager.add_right_spatial_tasks()
    task_manager.add_tracking_tasks()
    # task_manager.add_norm_velocity_tasks()
    task_manager.add_velocity_tasks()
    task_manager.add_distance_task()
    task_manager.add_velocity_profile_task()
    task_manager.add_mass_profile_task()

    i = 0

    snapshots = Snapshot.from_fits(config['input_file'])

    logging.info('i\tT, Myr\tTcomp\tTsave')

    for snapshot in snapshots:
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
        
        i += 1
