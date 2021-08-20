from typing import Any, Callable, List, Tuple

from amuse.lab import units
from archeology.analysis.tasks import (AbstractTask,
                                       AngularMomentumTask, CMDistanceTask,
                                       CMTrackTask, NormalVelocityTask,
                                       PlaneDirectionTask,
                                       PlaneSpatialScatterTask,
                                       PlaneVelocityScatterTask,
                                       SpatialScatterTask, VelocityProfileTask)
from archeology.analysis.utils import DrawParameters, get_galactic_basis
from archeology.datamodel import Snapshot


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

class VisualTask:
    def __init__(self, 
        axes_id: int, 
        task: AbstractTask,
        part: slice = slice(0, None),
        draw_params: DrawParameters = DrawParameters()
    ):
        self.axes_id = axes_id
        self.task = task
        self.part = part
        self.draw_params = draw_params

    def run(self, snapshot: Snapshot):
        return self.task.run(snapshot[self.part])

class TaskManager:
    def __init__(self) -> None:
        self.tasks = []
        self.updates = []

    def add_tasks(self, *visual_tasks):
        vtask: VisualTask
        for vtask in visual_tasks:
            self.tasks.append(vtask)

    def get_tasks(self) -> List[VisualTask]:
        return self.tasks

    def add_update(self, update: Callable[[Snapshot], Any]):
        self.updates.append(update)

    def update_tasks(self, snapshot: Snapshot):
        for update in self.updates:
            update(snapshot)

    def add_spatial_tasks(self):
        zy_task = VisualTask(
            0, SpatialScatterTask(('z', 'y'))
        )
        gal_plane_task = VisualTask(
            1, PlaneSpatialScatterTask(('z', 'y'))
        )

        zy_task.task.set_density_mode(700, (-60, 60, -55, 55))
        gal_plane_task.task.set_density_mode(700, (-60, 60, -55, 55))

        zy_task.draw_params = DrawParameters(
            extent = [-60, 60, -55, 55]
        )
        gal_plane_task.draw_params = DrawParameters(
            extent = [-60, 60, -55, 55]
        )

        self.add_tasks(zy_task, gal_plane_task)
        
    def add_tracking_tasks(self):
        host_xy_track_task = VisualTask(
            0, CMTrackTask(('x', 'y')), slice(200000), 
            DrawParameters(linestyle = 'solid', color = 'g', marker = 'None')
        )

        sat_xy_track_task = VisualTask(
            0, CMTrackTask(('x', 'y')), slice(200000, None),
            DrawParameters(linestyle = 'solid', color = 'y', marker = 'None')
        )

        host_zy_track_task = VisualTask(
            1, CMTrackTask(('z', 'y')), slice(200000),
            DrawParameters(linestyle = 'solid', color = 'g', marker = 'None')
        )

        sat_zy_track_task = VisualTask(
            1, CMTrackTask(('z', 'y')), slice(200000, None),
            DrawParameters(linestyle = 'solid', color = 'y', marker = 'None')
        )

        self.add_tasks(
            host_xy_track_task, 
            sat_xy_track_task, 
            host_zy_track_task, 
            sat_zy_track_task
        )

    def add_angular_momentum_task(self):
        xy_ang_momentum_task = VisualTask(
            0, AngularMomentumTask(('z', 'y'), 1000), slice(200000),
            DrawParameters(linestyle = 'solid', marker = 'None')
        )
        xy_plane_direction_task = VisualTask(
            0, PlaneDirectionTask(('z', 'y'), 1000), slice(200000),
            DrawParameters(linestyle = 'solid', marker = 'None')
        )

        zy_ang_momentum_task = VisualTask(
            1, AngularMomentumTask(('z', 'y'), 1000), slice(200000),
            DrawParameters(linestyle = 'solid', marker = 'None')
        )
        zy_plane_direction_task = VisualTask(
            1, PlaneDirectionTask(('z', 'y'), 1000), slice(200000),
            DrawParameters(linestyle = 'solid', marker = 'None')
        )

        self.add_tasks(
            xy_ang_momentum_task, 
            xy_plane_direction_task
        )

    def add_norm_velocity_tasks(self):
        host_norm_vel_task = VisualTask(
            2, 
            NormalVelocityTask(
                pov = [8, 0, 0] | units.kpc, 
                pov_velocity = [0, 200, 0] | units.kms,
                radius = 3 | units.kpc
            ), 
            slice(200000),
            DrawParameters(markersize = 0.2, color = 'b')
        )
        sat_norm_vel_task = VisualTask(
            2, 
            NormalVelocityTask(
                pov = [8, 0, 0] | units.kpc, 
                pov_velocity = [0, 200, 0] | units.kms,
                radius = 3 | units.kpc
            ),
            slice(200000, None),
            DrawParameters(markersize = 0.2, color = 'r')
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

            host_norm_vel_task.task.set_pov(sun_pos, sun_vel)
            sat_norm_vel_task.task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)
        self.add_tasks(
            host_norm_vel_task, 
            sat_norm_vel_task
        )

    def add_velocity_tasks(self):
        vxvy_host_task = VisualTask(
            3, PlaneVelocityScatterTask(('x', 'y')), 
            draw_params = DrawParameters(
                markersize = 0.02, color = 'b', extent = (-400, 400, -400, 400)
            )
        )

        vxvy_host_task.task.set_density_mode(700, (-400, 400, -400, 400))

        self.add_tasks(vxvy_host_task)

    def add_distance_task(self):
        dist_task = VisualTask(
            4, CMDistanceTask(slice(0, 200000, None), slice(200000, None, None)),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'r'
            )   
        )

        self.add_tasks(dist_task)

    def add_velocity_profile_task(self):
        host_vel_profile_task = VisualTask(
            5, VelocityProfileTask(), slice(200000),
            DrawParameters(
                linestyle = 'solid', color = 'r', 
                marker = 'None', label = 'host'
            )
        )

        sat_vel_profile_task = VisualTask(
            5, VelocityProfileTask(), slice(200000, None),
            DrawParameters(
                linestyle = 'solid', color = 'g', 
                marker = 'None', label = 'sat'
            )
        )
        
        sum_vel_profile_task = VisualTask(
            5, VelocityProfileTask(), 
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'b', 
                marker = 'None', label = 'all'
            )
        )

        self.add_tasks(
            host_vel_profile_task, 
            sat_vel_profile_task,
            sum_vel_profile_task
        )
