from typing import Any, Callable, Tuple

from amuse.lab import units
from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot

from tasks.abstract_visualizer_task import (AbstractVisualizerTask,
                                            NormalVelocityTask,
                                            PlaneDensityTask,
                                            SliceAngularMomentumTask,
                                            SlicedCMTrackTask, VProjectionTask)


class TaskManager:
    def __init__(self, number_of_axes: int) -> None:
        self.axes = {}
        self.updates = []

        for i in range(number_of_axes):
            self.axes[i] = []

    def get_tasks(self) -> Tuple[Tuple[int, AbstractVisualizerTask], ...]:
        res = []

        for (ax, lst) in self.axes.items():
            for task in lst:
                res.append((ax, task))

        return tuple(res)

    def update_tasks(self, snapshot: Snapshot):
        for update in self.updates:
            update(snapshot)

    def add_update(self, update: Callable[[Snapshot], Any]):
        self.updates.append(update)

    def add_task(self, axes_id: int,
        task: AbstractVisualizerTask, 
        plot_params: PlotParameters, 
        draw_params: DrawParameters
    ):
        task.plot_params = plot_params
        task.draw_params = draw_params
        self.axes[axes_id].append(task)

    def add_density_tasks(self):
        xy_task = PlaneDensityTask(('x', 'y'), (-100, 100, -120, 120), 700)
        zy_task = PlaneDensityTask(('z', 'y'), (-100, 100, -120, 120), 700)

        xy_task.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc'
        )
        zy_task.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = [] 
        )

        xy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120]
        )
        zy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120]
        )

        self.axes[0].append(xy_task)
        self.axes[1].append(zy_task)

    def add_tracking_tasks(self):
        hostxytracktask = SlicedCMTrackTask(('x', 'y'), (0, 200000))
        hostxytracktask.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc'
        )
        hostxytracktask.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('g', ),
            marker = 'None'
        )

        satxytracktask = SlicedCMTrackTask(('x', 'y'), (200000, -1))
        satxytracktask.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc'
        )
        satxytracktask.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('y', ),
            marker = 'None'
        )

        self.axes[0].append(hostxytracktask)
        self.axes[0].append(satxytracktask)

    def add_angular_momentum_task(self):
        ang_momentum_task = SliceAngularMomentumTask(('z', 'y'), (0, 200000), 1000)
        ang_momentum_task.plot_params = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = [] 
        )
        ang_momentum_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )

        self.axes[1].append(ang_momentum_task)

    def add_velocity_tasks(self):
        norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 5 | units.kpc
        )
        vxvy_task = VProjectionTask(('x', 'y'))

        norm_vel_task.plot_params = PlotParameters(
            xlim = (-600, 600), ylim = (0, 400),
            xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
        )
        vxvy_task.plot_params = PlotParameters(
            xlim = (-400, 400), ylim = (-400, 400),
            xlabel = '$V_x$, km/s', ylabel = '$V_y$, km/s'
        )

        norm_vel_task.draw_params = DrawParameters(
            markersize = 0.1,
            blocks_color = ('b', 'r')
        )
        vxvy_task.draw_params = DrawParameters(
            markersize = 0.02, blocks_color = ('b', 'r')
        )

        norm_vel_task.blocks = ((0, 200000), (200000, -1))
        vxvy_task.blocks = ((0, 200000), (200000, -1))

        def update_norm_velocity(snapshot: Snapshot):
            sun_pos = snapshot.particles[0:200000].center_of_mass() + ([8, 0, 0] | units.kpc)
            sun_vel = snapshot.particles[0:200000].center_of_mass_velocity() + ([0, 200, 0] | units.kms)
            norm_vel_task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)

        self.axes[2].append(norm_vel_task)
        self.axes[3].append(vxvy_task)
