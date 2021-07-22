from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from amuse.lab import units

from iotools.abstractiomanager import AbstractIOManager, NEMOIOManager
from tasks.abstract_visualizer_task import AbstractVisualizerTask
from tasks.task_manager import TaskManager
from utils.snapshot import Snapshot
from utils.visualizer import Visualizer

plt.style.use('ggplot')

def run(
    iomanager: AbstractIOManager,
    tasks: list,
    visualizer: Visualizer,
    update_tasks: Callable[[Snapshot], None]  
):
    i = 0

    while (iomanager.next_frame()):
        snapshot = iomanager.get_data()
        time = snapshot.timestamp.value_in(units.Myr)
        update_tasks(snapshot)
        snapshot = snapshot[0: 200000] + snapshot[1000000:1100000]

        task: AbstractVisualizerTask
        for (axes_id, task) in tasks:
            visualizer.set_plot_parameters(axes_id, task.plot_params)
            data = task.run(snapshot)
            visualizer.plot_points(axes_id, data, task.draw_params, task.blocks)

        visualizer.set_title('Time: {:.02f} Myr'.format(time))
        visualizer.save('output/img-{:03d}.png'.format(i))
        
        i += 1

visualizer = Visualizer()
visualizer.setup_grid(2)
visualizer.set_figsize(22, 10)

task_manager = TaskManager(4)
task_manager.add_density_tasks()
task_manager.add_tracking_tasks()
task_manager.add_angular_momentum_task()
task_manager.add_velocity_tasks()

run(
    NEMOIOManager('output/new_out.nemo'),
    task_manager.get_tasks(),
    visualizer,
    task_manager.update_tasks
)
