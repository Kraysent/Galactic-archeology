from typing import Callable
import matplotlib.pyplot as plt
import numpy as np
from amuse.lab import units

from iotools.abstractiomanager import AbstractIOManager, NEMOIOManager
from tasks.abstract_visualizer_task import (AbstractVisualizerTask, EnergyTask,
                                            NormalVelocityTask, VxVyTask,
                                            XYTask, ZYTask)
from utils.plot_parameters import PlotParameters
from utils.snapshot import Snapshot
from utils.visualizer import Visualizer

plt.style.use('ggplot')

def run(
    iomanager: AbstractIOManager,
    tasks: list,
    visualizer: Visualizer,
    update_tasks: Callable[[Snapshot], None]  
):
    while (iomanager.next_frame()):
        snapshot = iomanager.get_data()
        time = snapshot.timestamp.value_in(units.Myr)
        update_tasks(snapshot)
        snapshot.particles = snapshot.particles[0: 200000] + snapshot.particles[1000000:1100000]

        task: AbstractVisualizerTask
        for task in tasks:
            visualizer.set_plot_parameters(task.plot_params)
            (x_data, y_data) = task.run(snapshot)
            visualizer.plot_points(task.plot_params.axes_id, x_data, y_data, task.get_draw_params())

        visualizer.set_title('Time: {:.02f} Myr'.format(time))
        visualizer.save('output/{:.02f}.png'.format(time))

visualizer = Visualizer()
visualizer.setup_grid(2)
visualizer.set_figsize(22, 10)

class TaskHolder:
    def get_tasks(self) -> list:
        self.xytask = XYTask()
        self.xytask.plot_params = PlotParameters(
            axes_id = 0,
            xlim = (-150, 150), ylim = (-190, 190),
            xlabel = 'x, kpc', ylabel = 'y, kpc' 
        )

        self.zytask = ZYTask()
        self.zytask.plot_params = PlotParameters(
            axes_id = 1,
            xlim = (-150, 150), ylim = (-190, 190),
            xlabel = 'z, kpc', yticks = []
        )    

        self.norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 15 | units.kpc,
            emph = (200000, -1)
        )
        self.norm_vel_task.plot_params = PlotParameters(
            axes_id = 2, 
            xlim = (-600, 600), ylim = (0, 400),
            xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
        )

        self.vxvytask = VxVyTask()
        self.vxvytask.plot_params = PlotParameters(
            axes_id = 3,
            xlim = (-400, 400), ylim = (-400, 400),
            xlabel = '$V_x$, km/s', ylabel = '$V_y$, km/s'
        )

        return [self.xytask, self.zytask, self.norm_vel_task, self.vxvytask]

    def update_tasks(self, snapshot: Snapshot):
        sun_pos = snapshot.particles[0:200000].center_of_mass() + ([8, 0, 0] | units.kpc)
        sun_vel = snapshot.particles[0:200000].center_of_mass_velocity() + ([0, 200, 0] | units.kms)

        self.norm_vel_task.set_pov(sun_pos, sun_vel)

task_holder = TaskHolder()

run(
    NEMOIOManager('output/sum_out.nemo'),
    task_holder.get_tasks(),
    visualizer,
    task_holder.update_tasks
)
