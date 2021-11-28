from amuse.lab import units
from archeology.analysis.tasks import (DistanceTask, MassProfileTask,
                                       NormalVelocityTask, PointEmphasisTask,
                                       SpatialScatterTask, VelocityProfileTask,
                                       VelocityScatterTask, get_unit_vectors)
from archeology.analysis.utils import get_galactic_basis
from archeology.analysis.visual.nbody_object import NbodyObject
from archeology.analysis.visual.plot_parameters import DrawParameters
from archeology.analysis.visual.visual_task import VisualTask
from archeology.datamodel import Snapshot


class TaskManager:
    def __init__(self) -> None:
        self.tasks = []
        self.objects = [
            NbodyObject('b', 'host', slice(0, 1000000)),
            NbodyObject('r', 'satellite', slice(1000001, None))
        ]

    def add_tasks(self, *visual_tasks):
        vtask: VisualTask
        for vtask in visual_tasks:
            self.tasks.append(vtask)

    def get_tasks(self) -> list[VisualTask]:
        return self.tasks

    def add_left_spatial_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                0, SpatialScatterTask(*get_unit_vectors('zy')), obj.whole_part
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
                1, SpatialScatterTask(*get_unit_vectors('xy')), obj.whole_part
            )
            curr.task.set_density_mode(700, (-45, 45, -40, 40))
            curr.draw_params = DrawParameters(
                extent = [-45, 45, -40, 40],
                channel = obj.color
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_tracking_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                0, PointEmphasisTask(obj.whole_part.start, *get_unit_vectors('zy')),
                draw_params = DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            tasks.append(curr)

            curr = VisualTask(
                1, PointEmphasisTask(obj.whole_part.start, *get_unit_vectors('xy')),
                draw_params = DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_norm_velocity_tasks(self):
        def update_norm_velocity(snapshot: Snapshot):
            particles = snapshot.particles
            cm = particles.center_of_mass()
            cm_vel = particles.center_of_mass_velocity()

            (e1, e2, e3) = get_galactic_basis(snapshot)

            r = 8 | units.kpc
            v = -200 | units.kms

            sun_pos = cm + e2 * r
            sun_vel = cm_vel + e3 * v

            return sun_pos, sun_vel

        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                2, 
                NormalVelocityTask(
                    update_norm_velocity,
                    radius = 3 | units.kpc
                ), 
                obj.whole_part,
                DrawParameters(markersize = 0.2, color = obj.color)
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_velocity_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                3, VelocityScatterTask(*get_unit_vectors('xy')), obj.whole_part,
                DrawParameters(
                    markersize = 0.02, channel = obj.color, extent = (-400, 400, -400, 400)
                )
            )
            curr.task.set_density_mode(700, (-400, 400, -400, 400))
            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_distance_task(self):
        curr = VisualTask(
            4, DistanceTask(self.objects[0].whole_part.start, self.objects[1].whole_part.start),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'r'
            )   
        )

        self.add_tasks(curr)

    def add_velocity_profile_task(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(
                5, VelocityProfileTask(), obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'None', label = obj.label
                )
            )

            tasks.append(curr)

        curr = VisualTask(
            5, VelocityProfileTask(),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

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

            tasks.append(curr)

        curr = VisualTask(
            6, MassProfileTask(), 
            (self.objects[0].whole_part, self.objects[1].whole_part),
            DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        self.add_tasks(*tasks, curr)

