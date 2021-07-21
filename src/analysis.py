from typing import Callable
import matplotlib.pyplot as plt
import numpy as np
from amuse.lab import units

from iotools.abstractiomanager import AbstractIOManager, NEMOIOManager
from tasks.abstract_visualizer_task import (AbstractVisualizerTask, EnergyTask,
                                            NormalVelocityTask, PlaneDensityTask, VxVyTask, XYDensityTask, XYSliceCMTrackTask,
                                            XYTask, ZYDensityTask, ZYTask)
from utils.plot_parameters import DrawParameters, PlotParameters
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
        snapshot.particles = snapshot.particles[0: 200000] + snapshot.particles[1000000:1100000]

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

class TaskHolder:
    def get_tasks(self) -> list:
        self.xytask = XYTask()
        self.xytask.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc' 
        )
        self.xytask.draw_params = DrawParameters(
            blocks_color = ('b', 'r'),
            markersize = 0.05
        )
        self.xytask.blocks = ((0, 200000), (200000, -1))

        self.hostxytracktask = XYSliceCMTrackTask((0, 200000))
        self.hostxytracktask.plot_params = self.xytask.plot_params
        self.hostxytracktask.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('g', ),
            marker = 'None'
        )
        self.satxytracktask = XYSliceCMTrackTask((200000, -1))
        self.satxytracktask.plot_params = self.xytask.plot_params
        self.satxytracktask.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('y', ),
            marker = 'None'
        )

        self.xydensitytask = PlaneDensityTask(('x', 'y'), (-100, 100, -120, 120), 1000)
        self.xydensitytask.plot_params = PlotParameters(
            xlabel = 'x, kpc', ylabel = 'y, kpc' 
        )
        self.xydensitytask.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120]
        )

        self.zydensitytask = PlaneDensityTask(('z', 'y'), (-100, 100, -120, 120), 1000)
        self.zydensitytask.plot_params = PlotParameters(
            xlabel = 'z, kpc', ylabel = 'y, kpc' 
        )
        self.zydensitytask.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120]
        )

        self.zytask = ZYTask()
        self.zytask.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = []
        )
        self.zytask.draw_params = DrawParameters(
            blocks_color = ('b', 'r'),
            markersize = 0.05
        )
        self.zytask.blocks = ((0, 200000), (200000, -1))

        self.norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 5 | units.kpc
        )
        self.norm_vel_task.plot_params = PlotParameters(
            xlim = (-600, 600), ylim = (0, 400),
            xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
        )
        self.norm_vel_task.draw_params = DrawParameters(
            markersize = 0.1,
            blocks_color = ('b', 'r')
        )
        self.norm_vel_task.blocks = ((0, 200000), (200000, -1))

        self.vxvytask = VxVyTask()
        self.vxvytask.plot_params = PlotParameters(
            xlim = (-400, 400), ylim = (-400, 400),
            xlabel = '$V_x$, km/s', ylabel = '$V_y$, km/s'
        )
        self.vxvytask.draw_params = DrawParameters(
            markersize = 0.02, blocks_color = ('b', 'r')
        )
        self.vxvytask.blocks = ((0, 200000), (200000, -1))

        return [
            # (0, self.xytask), 
            # (0, self.hostxytracktask), 
            # (0, self.satxytracktask),
            (0, self.xydensitytask),
            (1, self.zydensitytask),
            # (1, self.zytask),
            (2, self.norm_vel_task), 
            (3, self.vxvytask)
        ]

    def update_tasks(self, snapshot: Snapshot):
        sun_pos = snapshot.particles[0:200000].center_of_mass() + ([8, 0, 0] | units.kpc)
        sun_vel = snapshot.particles[0:200000].center_of_mass_velocity() + ([0, 200, 0] | units.kms)

        self.norm_vel_task.set_pov(sun_pos, sun_vel)

task_holder = TaskHolder()

run(
    NEMOIOManager('output/new_out.nemo'),
    task_holder.get_tasks(),
    visualizer,
    task_holder.update_tasks
)
