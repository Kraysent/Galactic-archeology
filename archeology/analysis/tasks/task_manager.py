from typing import Any, Callable, List

import numpy as np
from amuse.lab import units
from archeology.analysis import utils
from archeology.analysis.tasks import (AbstractTask, AngularMomentumTask,
                                       CMDistanceTask, NormalVelocityTask,
                                       PlaneDirectionTask, SpatialScatterTask,
                                       VelocityProfileTask)
from archeology.analysis.tasks.abstract_task import (VectorTrackTask,
                                                     VelocityScatterTask,
                                                     get_unit_vectors)
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

class NbodyObject:
    def __init__(self,
        part: slice,
        color: str = 'r',
        label: str = ''
    ) -> None:
        self.part = part
        self.color = color
        self.label = label

class TaskManager:
    def __init__(self) -> None:
        self.tasks = []
        self.updates = []
        self.objects = [
            NbodyObject(slice(200000), 'r', 'host'),
            NbodyObject(slice(200000, None), 'g', 'satellite')
        ]

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

    def add_left_spatial_tasks(self):
        tasks = []

        for object in self.objects:
            curr = VisualTask(
                0, SpatialScatterTask(*get_unit_vectors('zy')), object.part
            )
            curr.task.set_density_mode(700, (-45, 45, -40, 40))
            curr.draw_params = DrawParameters(
                extent = [-45, 45, -40, 40],
                channel = object.color
            )

            tasks.append(curr)
            
        self.add_tasks(*tasks)
        
    def add_right_spatial_tasks(self):
        tasks = []

        for object in self.objects:
            curr = VisualTask(
                1, SpatialScatterTask(*get_unit_vectors('xy')), object.part
            )
            curr.task.set_density_mode(700, (-45, 45, -40, 40))
            curr.draw_params = DrawParameters(
                extent = [-45, 45, -40, 40],
                channel = object.color
            )

            tasks.append(curr)

        def update_galactic_plane(snapshot: Snapshot):
            gal_basis = utils.get_galactic_basis(snapshot)

            for task in tasks:
                task.task.update_basis(gal_basis[1], gal_basis[2])

        self.add_update(update_galactic_plane)
        self.add_tasks(*tasks)

    def add_tracking_tasks(self):
        tasks = []

        for object in self.objects:
            curr = VisualTask(
                0, VectorTrackTask(*get_unit_vectors('zy')), object.part, 
                DrawParameters(
                    linestyle = 'solid', color = object.color, marker = 'None'
                )
            )

            tasks.append(curr)

        def update_cm_vectors(snapshot: Snapshot):
            for task in tasks:
                task.task.update_vector(
                    snapshot[task.part].particles.center_of_mass(), units.kpc
                )
        
        self.add_update(update_cm_vectors)
        self.add_tasks(*tasks)

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
        tasks = []

        for object in self.objects:
            curr = VisualTask(
                2, 
                NormalVelocityTask(
                    pov = [8, 0, 0] | units.kpc, 
                    pov_velocity = [0, 200, 0] | units.kms,
                    radius = 3 | units.kpc
                ), 
                object.part,
                DrawParameters(markersize = 0.2, color = object.color)
            )

            tasks.append(curr)

        def update_norm_velocity(snapshot: Snapshot):
            particles = snapshot[0:200000].particles
            cm = particles.center_of_mass()
            cm_vel = particles.center_of_mass_velocity()

            (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])

            r = 8 | units.kpc
            v = 200 | units.kms

            sun_pos = cm + e2 * r
            sun_vel = cm_vel + e3 * v

            for task in tasks:
                task.task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)
        self.add_tasks(*tasks)

    def add_velocity_tasks(self):
        tasks = []

        for object in self.objects:
            curr = VisualTask(
                3, VelocityScatterTask(*get_unit_vectors('xy')), object.part,
                DrawParameters(
                    markersize = 0.02, channel = object.color, extent = (-400, 400, -400, 400)
                )
            )
            curr.task.set_density_mode(700, (-400, 400, -400, 400))
            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_distance_task(self):
        dist_task = VisualTask(
            4, CMDistanceTask(slice(0, 200000, None), slice(200000, None, None)),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'r'
            )   
        )

        self.add_tasks(dist_task)

    def add_velocity_profile_task(self):
        tasks = []

        for object in self.objects:
            tasks.append(VisualTask(
                5, VelocityProfileTask(), object.part,
                DrawParameters(
                    linestyle = 'solid', color = object.color, 
                    marker = 'None', label = object.label
                )
            ))

        sum_vel_profile_task = VisualTask(
            5, VelocityProfileTask(), 
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        self.add_tasks(
            *tasks,
            sum_vel_profile_task
        )
