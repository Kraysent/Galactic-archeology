from typing import Any, Callable, List

from amuse.lab import units
from archeology.analysis import utils
from archeology.analysis.tasks import (AngularMomentumTask, DistanceTask,
                                       MassProfileTask, NormalVelocityTask,
                                       PlaneDirectionTask, PointEmphasisTask,
                                       SpatialScatterTask, VelocityProfileTask,
                                       VelocityScatterTask, get_unit_vectors)
from archeology.analysis.utils import DrawParameters, get_galactic_basis
from archeology.analysis.visual import VisualTask, NbodyObject
from archeology.datamodel import Snapshot


class TaskManager:
    def __init__(self) -> None:
        self.tasks = []
        self.updates = []
        self.objects = [
            NbodyObject(slice(200001), 'b', 'host', slice(1000000)),
            NbodyObject(slice(1000001, 1100002), 'r', 'satellite', slice(1000001, None))
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

        for obj in self.objects:
            curr = VisualTask(
                0, SpatialScatterTask(*get_unit_vectors('zy')), obj.part
            )
            curr.task.set_density_mode(700, (-45, 45, -40, 40))
            curr.draw_params = DrawParameters(
                extent = [-45, 45, -40, 40],
                channel = obj.color
            )

            tasks.append(curr)
            
        self.add_tasks(*tasks)

    def add_right_spatial_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                1, SpatialScatterTask(*get_unit_vectors('xy')), obj.part
            )
            curr.task.set_density_mode(700, (-45, 45, -40, 40))
            curr.draw_params = DrawParameters(
                extent = [-45, 45, -40, 40],
                channel = obj.color
            )

            def update_action(snapshot: Snapshot, curr = curr):
                gal_basis = utils.get_galactic_basis(snapshot)
                curr.task.update_basis(gal_basis[1], gal_basis[2])

            curr.action = update_action

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_tracking_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                0, PointEmphasisTask(*get_unit_vectors('zy')), obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            def update_action(snapshot: Snapshot, curr = curr):
                curr.task.update_vector(
                    snapshot[curr.part].particles[0].position, units.kpc
                )

            curr.action = update_action
            tasks.append(curr)

            curr = VisualTask(
                1, PointEmphasisTask(*get_unit_vectors('zy')), obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            def update_action(snapshot: Snapshot, curr = curr):
                gal_basis = utils.get_galactic_basis(snapshot)

                curr.task.update_vector(
                    snapshot[curr.part].particles[0].position, units.kpc
                )
                curr.task.update_basis(gal_basis[1], gal_basis[2])

            curr.action = update_action
            tasks.append(curr)

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

        for obj in self.objects:
            curr = VisualTask(
                2, 
                NormalVelocityTask(
                    pov = [8, 0, 0] | units.kpc, 
                    pov_velocity = [0, 200, 0] | units.kms,
                    radius = 3 | units.kpc
                ), 
                obj.part,
                DrawParameters(markersize = 0.2, color = obj.color)
            )

            tasks.append(curr)

        def update_norm_velocity(snapshot: Snapshot):
            particles = snapshot[0:200000].particles
            cm = particles.center_of_mass()
            cm_vel = particles.center_of_mass_velocity()

            (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])

            r = 8 | units.kpc
            v = -200 | units.kms

            sun_pos = cm + e2 * r
            sun_vel = cm_vel + e3 * v

            for task in tasks:
                task.task.set_pov(sun_pos, sun_vel)

        self.add_update(update_norm_velocity)
        self.add_tasks(*tasks)

    def add_velocity_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                3, VelocityScatterTask(*get_unit_vectors('xy')), obj.part,
                DrawParameters(
                    markersize = 0.02, channel = obj.color, extent = (-400, 400, -400, 400)
                )
            )
            curr.task.set_density_mode(700, (-400, 400, -400, 400))
            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_distance_task(self):
        curr = VisualTask(
            4, DistanceTask(),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'r'
            )   
        )

        def update_action(snapshot: Snapshot):
            curr.task.update_points(
                snapshot[self.objects[0].part].particles[0].position, 
                snapshot[self.objects[1].part].particles[0].position, 
                units.kpc
            )

        curr.action = update_action

        self.add_tasks(curr)

    def add_velocity_profile_task(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                5, VelocityProfileTask(), obj.part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'None', label = obj.label
                )
            )

            def update_action(snapshot: Snapshot, curr = curr):
                particles = curr.get_active_snapshot(snapshot).particles
                curr.task.update_center(particles.center_of_mass(), particles.center_of_mass_velocity())

            curr.action = update_action
            tasks.append(curr)

        curr = VisualTask(
            5, VelocityProfileTask(), 
            (self.objects[0].part, self.objects[1].part),
            DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        def update_action(snapshot: Snapshot, curr = curr):
            particles = snapshot.particles
            curr.task.update_center(particles.center_of_mass(), particles.center_of_mass_velocity())

        curr.action = update_action

        self.add_tasks(*tasks, curr)

    def add_mass_profile_task(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                6, MassProfileTask(), obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'None', label = obj.label
                )
            )

            def update_action(snapshot: Snapshot, curr = curr):
                particles = curr.get_active_snapshot(snapshot).particles
                curr.task.update_center(particles.center_of_mass())

            curr.action = update_action
            tasks.append(curr)

        curr = VisualTask(
            6, MassProfileTask(), 
            (self.objects[0].whole_part, self.objects[1].whole_part),
            DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        def update_action(snapshot: Snapshot, curr = curr):
            particles = snapshot.particles
            curr.task.update_center(particles.center_of_mass())

        curr.action = update_action

        self.add_tasks(*tasks, curr)

