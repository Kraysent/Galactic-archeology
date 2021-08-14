import time

import numpy as np
from amuse.lab import units

from archeology.analysis.tasks import AbstractVisualizerTask, TaskManager
from archeology.analysis.utils import Visualizer
from archeology.datamodel import Snapshot
from archeology.iotools import NEMOIOManager

visualizer = Visualizer()
visualizer.add_axes(0, 0.35, 0.35, 0.6)
visualizer.set_plot_parameters(0,
    xlim = (-60, 60), ylim = (-55, 55),
    xlabel = 'x, kpc', ylabel = 'y, kpc',
    xticks = [0, 10], yticks = [0, 10]
)

visualizer.add_axes(0.33, 0.35, 0.35, 0.6)
visualizer.set_plot_parameters(1,
    xlim = (-60, 60), ylim = (-55, 55),
    yticks = [], xticks = [0, 10]
)

visualizer.add_axes(0.72, 0.66, 0.14, 0.3)
visualizer.set_plot_parameters(2,
    xlim = (-600, 600), ylim = (0, 500),
    xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
)

visualizer.add_axes(0.72, 0.33, 0.14, 0.3)
visualizer.set_plot_parameters(3,
    xlim = (-400, 400), ylim = (-400, 400),
    xlabel = '$v_x$, km/s', ylabel = '$v_y$, km/s'
)

visualizer.add_axes(0, 0, 0.14, 0.3)
visualizer.set_plot_parameters(4,
    xlim = (0, 10000), ylim = (0, 150),
    xlabel = 'Time, Myr', ylabel = 'Separation, kpc',
    grid = True, yscale = 'log'
)

visualizer.add_axes(0.18, 0, 0.32, 0.3)
visualizer.set_plot_parameters(5,
    xlim = (0, 15), ylim = (0, 400),
    xlabel = '$r$, kpc', ylabel = '$v$, km/s',
    grid = True
)

# visualizer.add_axes(0.36, 0, 0.14, 0.3)
# visualizer.set_plot_parameters(6)

visualizer.add_axes(0.54, 0, 0.14, 0.3)
visualizer.set_plot_parameters(6)

visualizer.add_axes(0.72, 0, 0.14, 0.3)
visualizer.set_plot_parameters(7)

visualizer.set_figsize(20, 11)

iomanager = NEMOIOManager('output/models/model_out.nemo')

task_manager = TaskManager(visualizer.number_of_axes)

task_manager.add_spatial_tasks()
# task_manager.add_tracking_tasks()
task_manager.add_norm_velocity_tasks()
task_manager.add_angular_momentum_task()
task_manager.add_velocity_tasks()
task_manager.add_distance_task()
task_manager.add_velocity_profile_task()

i = 0

def extract_barion_matter(snapshot: Snapshot):
    return snapshot[0: 200000] + snapshot[1000000:1100000]

while (iomanager.next_frame()):
    start_comp = time.time()
    snapshot = extract_barion_matter(iomanager.get_data())
    
    task_manager.update_tasks(snapshot)

    task: AbstractVisualizerTask
    for (axes_id, task, part) in task_manager.get_tasks():
        data = task.run(snapshot[part])

        if type(data) is tuple:
            visualizer.scatter_points(axes_id, data, task.draw_params)
        else:
            visualizer.plot_image(axes_id, data, task.draw_params)

    timestamp = snapshot.timestamp.value_in(units.Myr)
    visualizer.set_title('Time: {:.02f} Myr'.format(timestamp))

    start_save = time.time()
    visualizer.save('output/img-{:03d}.png'.format(i))

    end = time.time()
    print(f'i: {i:03d}; C: {np.round(start_save - start_comp, 2):.02f}; S: {np.round(end - start_save, 2):.02f}')
    
    i += 1
