from typing import Any, Callable, List, Tuple

import numpy as np
from amuse.lab import units
from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot

from tasks.abstract_visualizer_task import (AbstractVisualizerTask,
                                            AngularMomentumTask, CMDistanceTask, CMTrackTask,
                                            NormalVelocityTask,
                                            PlaneDirectionTask,
                                            SpatialScatterTask,
                                            VelocityScatterTask)


def get_sun_position_and_velocity(snapshot: Snapshot):
    particles = snapshot[0:200000].particles
    r = particles.position.value_in(units.kpc)
    v = particles.velocity.value_in(units.kms)
    cm = particles.center_of_mass().value_in(units.kpc)
    cm_vel = particles.center_of_mass_velocity().value_in(units.kms)
    m = particles.mass.value_in(units.MSun)

    r = r - cm
    v = v - cm_vel
    specific_ang_momentum = m[:, np.newaxis] * np.cross(v, r)
    ang_momentum = np.sum(specific_ang_momentum, axis = 0)
    r = 8

    plane_vector = np.empty(ang_momentum.shape)
    plane_vector[0] = 1
    plane_vector[1] = 1
    plane_vector[2] = - plane_vector[0] * ang_momentum[0] / ang_momentum[2] - plane_vector[1] * ang_momentum[1] / ang_momentum[2] 

    length = (plane_vector ** 2).sum() ** 0.5
    plane_vector = plane_vector / length * r
    sun_pos = cm + plane_vector | units.kpc
    sun_vel = cm_vel + [0, 200, 0] | units.kms

    return sun_pos, sun_vel

class TaskManager:
    def __init__(self, number_of_axes: int) -> None:
        self.axes = {}
        self.updates = []

        for i in range(number_of_axes):
            self.axes[i] = []

    def add_tasks(self, axes_id: int, *tasks):
        for task in tasks:
            self.axes[axes_id].append(task)

    def get_tasks(self) -> List[Tuple[int, AbstractVisualizerTask]]:
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
            markersize = 0.3,
            color = 'b'
        )
        sat_norm_vel_task.draw_params = DrawParameters(
            markersize = 0.3,
            color = 'r'
        )

        def update_norm_velocity(snapshot: Snapshot):
            sun_pos, sun_vel = get_sun_position_and_velocity(snapshot)
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

    def add_distance_task(self):
        dist_task = CMDistanceTask(slice(0, 200000, None), slice(200000, None, None))
        dist_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'r'
        )

        self.add_tasks(4, dist_task)
