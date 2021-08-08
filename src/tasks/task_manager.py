from typing import Any, Callable, List, Tuple

from amuse.lab import units
from utils.galactic_utils import get_galactic_basis
from utils.plot_parameters import DrawParameters
from utils.snapshot import Snapshot

from tasks.abstract_visualizer_task import (AbstractVisualizerTask,
                                            AngularMomentumTask,
                                            CMDistanceTask, CMTrackTask,
                                            NormalVelocityTask,
                                            PlaneDirectionTask, PlaneSpatialScatterTask, PlaneVelocityScatterTask,
                                            SpatialScatterTask,
                                            VelocityScatterTask)


def get_sun_position_and_velocity(snapshot: Snapshot):
    particles = snapshot[0:200000].particles
    cm = particles.center_of_mass()
    cm_vel = particles.center_of_mass_velocity()

    (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])

    r = 8 | units.kpc
    v = 200 | units.kms

    sun_pos = cm + e2 * r
    sun_vel = cm_vel + e3 * v

    return sun_pos, sun_vel

class TaskManager:
    def __init__(self, number_of_axes: int) -> None:
        self.axes = {}
        self.updates = []

        for i in range(number_of_axes):
            self.axes[i] = []

    def add_tasks(self, axes_id: int, *sliced_tasks):
        for sliced_task in sliced_tasks:
            if type(sliced_task) is tuple:
                task, part = sliced_task
                self.axes[axes_id].append((task, part))
            else:
                self.axes[axes_id].append((sliced_task, slice(0, None)))

    def get_tasks(self) -> List[Tuple[int, AbstractVisualizerTask]]:
        for (ax, lst) in self.axes.items():
            for (task, part) in lst:
                yield ax, task, part

    def add_update(self, update: Callable[[Snapshot], Any]):
        self.updates.append(update)

    def update_tasks(self, snapshot: Snapshot):
        for update in self.updates:
            update(snapshot)

    def add_spatial_tasks(self):
        xy_task = SpatialScatterTask(('z', 'y'))
        zy_task = PlaneSpatialScatterTask(('z', 'y'))
        xy_task.set_density_mode(700, (-60, 60, -55, 55))
        zy_task.set_density_mode(700, (-60, 60, -55, 55))

        xy_task.draw_params = DrawParameters(
            extent = [-60, 60, -55, 55], cmap = 'ocean_r'
        )
        zy_task.draw_params = DrawParameters(
            extent = [-60, 60, -55, 55], cmap = 'ocean_r'
        )

        self.add_tasks(0, xy_task)
        self.add_tasks(1, zy_task)
        
    def add_tracking_tasks(self):
        host_xy_track_task = CMTrackTask(('x', 'y'))
        host_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'g', marker = 'None'
        )

        sat_xy_track_task = CMTrackTask(('x', 'y'))
        sat_xy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'y', marker = 'None'
        )

        host_zy_track_task = CMTrackTask(('z', 'y'))
        host_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'g', marker = 'None'
        )

        sat_zy_track_task = CMTrackTask(('z', 'y'))
        sat_zy_track_task.draw_params = DrawParameters(
            linestyle = 'solid', color = 'y', marker = 'None'
        )

        self.add_tasks(0, 
            (host_xy_track_task, slice(200000)), 
            (sat_xy_track_task, slice(200000, None))
        )
        self.add_tasks(1, 
            (host_zy_track_task, slice(200000)), 
            (sat_zy_track_task, slice(200000, None))
        )

    def add_angular_momentum_task(self):
        xy_ang_momentum_task = AngularMomentumTask(('z', 'y'), 1000)
        xy_ang_momentum_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )
        xy_plane_direction_task = PlaneDirectionTask(('z', 'y'), 1000)
        xy_plane_direction_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )

        zy_ang_momentum_task = AngularMomentumTask(('z', 'y'), 1000)
        zy_ang_momentum_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )
        zy_plane_direction_task = PlaneDirectionTask(('z', 'y'), 1000)
        zy_plane_direction_task.draw_params = DrawParameters(
            linestyle = 'solid', marker = 'None'
        )

        self.add_tasks(0, 
            (xy_ang_momentum_task, slice(200000)), 
            (xy_plane_direction_task, slice(200000))
        )
        # self.add_tasks(1, 
        #     (zy_ang_momentum_task, slice(200000)), 
        #     (zy_plane_direction_task, slice(200000))
        # )

    def add_norm_velocity_tasks(self):
        host_norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 3 | units.kpc
        )
        sat_norm_vel_task = NormalVelocityTask(
            pov = [8, 0, 0] | units.kpc, 
            pov_velocity = [0, 200, 0] | units.kms,
            radius = 3 | units.kpc
        )

        host_norm_vel_task.draw_params = DrawParameters(
            markersize = 0.2,
            color = 'b'
        )
        sat_norm_vel_task.draw_params = DrawParameters(
            markersize = 0.2,
            color = 'r'
        )

        def update_norm_velocity(snapshot: Snapshot):
            particles = snapshot[0:200000].particles
            cm = particles.center_of_mass()
            cm_vel = particles.center_of_mass_velocity()

            (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])

            r = 8 | units.kpc
            v = 200 | units.kms

            sun_pos = cm + e2 * r
            sun_vel = cm_vel + e3 * v

            host_norm_vel_task.set_pov(sun_pos, sun_vel)
            sat_norm_vel_task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)
        self.add_tasks(2, 
            (host_norm_vel_task, slice(200000)), 
            (sat_norm_vel_task, slice(200000, None))
        )

    def add_velocity_tasks(self):
        vxvy_host_task = PlaneVelocityScatterTask(('x', 'y'))

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
