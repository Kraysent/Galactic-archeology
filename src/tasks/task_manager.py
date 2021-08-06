from typing import Any, Callable, Tuple

from amuse.lab import units
from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot

from tasks.abstract_visualizer_task import (AbstractVisualizerTask,
                                            AngularMomentumTask, CMTrackTask,
                                            NormalVelocityTask, PlaneDirectionTask,
                                            SpatialScatterTask,
                                            VelocityScatterTask)


class TaskManager:
    def __init__(self, number_of_axes: int) -> None:
        self.axes = {}
        self.axes_styles = {}
        self.updates = []

        for i in range(number_of_axes):
            self.axes[i] = []
            self.axes_styles[i] = PlotParameters()

    def add_tasks(self, axes_id: int, *tasks):
        for task in tasks:
            self.axes[axes_id].append(task)

    def get_tasks(self) -> Tuple[Tuple[int, AbstractVisualizerTask], ...]:
        res = []

        for (ax, lst) in self.axes.items():
            for task in lst:
                res.append((ax, task))

        return res

    def add_update(self, update: Callable[[Snapshot], Any]):
        self.updates.append(update)

    def update_tasks(self, snapshot: Snapshot):
        for update in self.updates:
            update(snapshot)

    def set_axes_style(self, axes_id: int, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self.axes_styles[axes_id], key, value)

    def get_axes_style(self, axes_id: int):
        return self.axes_styles[axes_id]

    def add_spatial_tasks(self):
        xy_task = SpatialScatterTask(('x', 'y'))
        zy_task = SpatialScatterTask(('z', 'y'))
        xy_task.set_density_mode(700, (-100, 100, -120, 120))
        zy_task.set_density_mode(700, (-100, 100, -120, 120))

        xy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120], cmap = 'ocean_r'
        )
        zy_task.draw_params = DrawParameters(
            extent = [-100, 100, -120, 120], cmap = 'ocean_r'
        )

        self.add_tasks(1, zy_task)
        self.add_tasks(0, xy_task)
        
    def add_tracking_tasks(self):
        host_xy_track_task = CMTrackTask(('x', 'y'), slice(0, 200000, None))
        host_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'g', marker = 'None'
        )

        sat_xy_track_task = CMTrackTask(('x', 'y'), slice(200000, None, None))
        sat_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'y', marker = 'None'
        )

        host_zy_track_task = CMTrackTask(('z', 'y'), slice(0, 200000, None))
        host_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'g', marker = 'None'
        )

        sat_zy_track_task = CMTrackTask(('z', 'y'), slice(200000, None, None))
        sat_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'y', marker = 'None'
        )

        self.add_tasks(0, host_xy_track_task, sat_xy_track_task)
        self.add_tasks(1, host_zy_track_task, sat_zy_track_task)

    def add_angular_momentum_task(self):
        ang_momentum_task = AngularMomentumTask(('z', 'y'), 1000, slice(0, 200000, None))
        ang_momentum_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )
        plane_direction_task = PlaneDirectionTask(('z', 'y'), 1000, slice(0, 200000, None))
        plane_direction_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )

        self.add_tasks(1, ang_momentum_task, plane_direction_task)

    def add_norm_velocity_tasks(self):
        host_norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 5 | units.kpc,
            part = slice(0, 200000, None)
        )
        sat_norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 5 | units.kpc,
            part = slice(200000, None, None)
        )

        host_norm_vel_task.draw_params = DrawParameters(
            markersize = 0.1,
            color = 'b'
        )
        sat_norm_vel_task.draw_params = DrawParameters(
            markersize = 0.1,
            color = 'r'
        )

        def update_norm_velocity(snapshot: Snapshot):
            sun_pos = snapshot.particles[0:200000].center_of_mass() + ([8, 0, 0] | units.kpc)
            sun_vel = snapshot.particles[0:200000].center_of_mass_velocity() + ([0, 200, 0] | units.kms)
            host_norm_vel_task.set_pov(sun_pos, sun_vel)
            sat_norm_vel_task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)
        self.add_tasks(2, host_norm_vel_task, sat_norm_vel_task)

    def add_velocity_tasks(self):
        vxvy_host_task = VelocityScatterTask(('x', 'y'))

        vxvy_host_task.set_density_mode(700, (-400, 400, -400, 400))
        vxvy_host_task.draw_params = DrawParameters(
            markersize = 0.02, color = 'b', extent = (-400, 400, -400, 400)
        )

        self.add_tasks(3, vxvy_host_task)
