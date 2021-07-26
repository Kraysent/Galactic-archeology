from typing import Any, Callable, Tuple

from amuse.lab import units
from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot

from tasks.abstract_visualizer_task import (AbstractVisualizerTask,
                                            AngularMomentumTask, CMTrackTask,
                                            NormalVelocityTask,
                                            PlaneDensityTask, VProjectionTask)


class TaskManager:
    def __init__(self, number_of_axes: int) -> None:
        self.axes = {}
        self.axes_styles = {}
        self.updates = []

        for i in range(number_of_axes):
            self.axes[i] = []
            self.axes_styles[i] = PlotParameters()

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

    def set_axes_style(self, axes_id: int, params: PlotParameters):
        self.axes_styles[axes_id] = params

    def get_axes_style(self, axes_id: int):
        return self.axes_styles[axes_id]

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

        xy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120], cmap = 'ocean_r'
        )
        zy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120], cmap = 'ocean_r'
        )

        self.axes[0].append(xy_task)
        self.axes[1].append(zy_task)

        xy_style = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc'
        )
        zy_style = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = [] 
        )

        self.set_axes_style(0, xy_style)
        self.set_axes_style(1, zy_style)

    def add_tracking_tasks(self):
        host_xy_track_task = CMTrackTask(('x', 'y'), (0, 200000))
        host_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('g', ),
            marker = 'None'
        )

        sat_xy_track_task = CMTrackTask(('x', 'y'), (200000, -1))
        sat_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('y', ),
            marker = 'None'
        )

        host_zy_track_task = CMTrackTask(('z', 'y'), (0, 200000))
        host_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('g', ),
            marker = 'None'
        )

        sat_zy_track_task = CMTrackTask(('z', 'y'), (200000, -1))
        sat_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid',
            blocks_color = ('y', ),
            marker = 'None'
        )

        self.axes[0].append(host_xy_track_task)
        self.axes[0].append(sat_xy_track_task)
        self.axes[1].append(host_zy_track_task)
        self.axes[1].append(sat_zy_track_task)

        xy_axes_style = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'x, kpc', ylabel = 'y, kpc'
        )
        zy_axes_style = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = []
        )

        self.set_axes_style(0, xy_axes_style)

    def add_angular_momentum_task(self):
        ang_momentum_task = AngularMomentumTask(('z', 'y'), (0, 200000), 1000)
        ang_momentum_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )

        self.axes[1].append(ang_momentum_task)

        axes_style = PlotParameters(
            xlim = (-100, 100), ylim = (-120, 120),
            xlabel = 'z, kpc', yticks = [] 
        )

        self.set_axes_style(1, axes_style)

    def add_velocity_tasks(self):
        norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 5 | units.kpc
        )
        vxvy_task = VProjectionTask(('x', 'y'))

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

        norm_vel_style = PlotParameters(
            xlim = (-600, 600), ylim = (0, 400),
            xlabel = '$v_r$, km/s', ylabel = '$v_{\\tau}$, km/s'
        )
        vxvy_style = PlotParameters(
            xlim = (-400, 400), ylim = (-400, 400),
            xlabel = '$V_x$, km/s', ylabel = '$V_y$, km/s'
        )

        self.set_axes_style(2, norm_vel_style)
        self.set_axes_style(3, vxvy_style)

