from amuse.lab import units

from iotools.abstractiomanager import NEMOIOManager
from tasks.abstract_visualizer_task import AbstractVisualizerTask
from tasks.task_manager import TaskManager
from utils.visualizer import Visualizer

visualizer = Visualizer()
visualizer.add_axes(0, 0, 0.33, 1)
visualizer.add_axes(0.33, 0, 0.33, 1)
visualizer.add_axes(0.7, 0.5, 0.25, 0.45)
visualizer.add_axes(0.68, 0, 0.3, 0.45)
visualizer.set_figsize(22, 10)

iomanager = NEMOIOManager('output/new_out.nemo')

task_manager = TaskManager(visualizer.number_of_axes)

task_manager.set_axes_style(0,
    xlim = (-100, 100), ylim = (-120, 120),
    xlabel = 'x, kpc', ylabel = 'y, kpc'
)
task_manager.set_axes_style(1,
    xlim = (-100, 100), ylim = (-120, 120),
    xlabel = 'z, kpc', yticks = [] 
)
task_manager.set_axes_style(2,
    xlim = (-600, 600), ylim = (0, 500),
    xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
)
task_manager.set_axes_style(3,
    xlim = (-400, 400), ylim = (-400, 400),
    xlabel = '$V_x$, km/s', ylabel = '$V_y$, km/s'
)

task_manager.add_spatial_tasks()
# task_manager.add_tracking_tasks()
task_manager.add_norm_velocity_tasks()
task_manager.add_angular_momentum_task()
task_manager.add_velocity_tasks()

i = 0

while (iomanager.next_frame()):
    snapshot = iomanager.get_data()
    snapshot = snapshot[0: 200000] + snapshot[1000000:1100000]
    time = snapshot.timestamp.value_in(units.Myr)
    task_manager.update_tasks(snapshot)

    for j in range(visualizer.number_of_axes):
        visualizer.set_plot_parameters(j, task_manager.get_axes_style(j))

    task: AbstractVisualizerTask
    for (axes_id, task) in task_manager.get_tasks():
        data = task.execute(snapshot)

        if type(data) is tuple:
            visualizer.scatter_points(axes_id, data, task.draw_params)
        else:
            visualizer.plot_image(axes_id, data, task.draw_params)

    visualizer.set_title('Time: {:.02f} Myr'.format(time))
    visualizer.save('output/img-{:03d}.png'.format(i))
    
    i += 1
