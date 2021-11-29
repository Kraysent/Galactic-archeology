from amuse.lab import units
from archeology.analysis.tasks import (DistanceTask, MassProfileTask,
                                       PointEmphasisTask, SpatialScatterTask,
                                       VelocityProfileTask,
                                       VelocityScatterTask)
from archeology.analysis.visual.nbody_object import NbodyObject
from archeology.analysis.visual.plot_parameters import DrawParameters
from archeology.analysis.visual.visual_task import VisualTask


class TaskManager:
    def __init__(self, objects: list[NbodyObject]) -> None:
        self.tasks = []
        self.objects = objects

    def add_tasks(self, *visual_tasks):
        vtask: VisualTask
        for vtask in visual_tasks:
            self.tasks.append(vtask)

    def get_tasks(self) -> list[VisualTask]:
        return self.tasks

    def add_left_spatial_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(0, 
                SpatialScatterTask(
                    [0, 0, 1] | units.kpc,
                    [0, 1, 0] | units.kpc
                ), 
                obj.whole_part,
                DrawParameters(
                    extent = [-45, 45, -40, 40],
                    channel = obj.color,
                    is_density_plot = True,
                    resolution = 700
                )
            )

            tasks.append(curr)
            
        self.add_tasks(*tasks)

    def add_right_spatial_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(1, 
                SpatialScatterTask(
                    [1, 0, 0] | units.kpc,
                    [0, 1, 0] | units.kpc
                ), 
                obj.whole_part,
                DrawParameters(
                    extent = [-45, 45, -40, 40],
                    channel = obj.color,
                    is_density_plot = True,
                    resolution = 700
                )
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_tracking_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(0, 
                PointEmphasisTask(
                    obj.whole_part.start, 
                    [0, 0, 1] | units.kpc,
                    [0, 1, 0] | units.kpc
                ),
                draw_params = DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            tasks.append(curr)

            curr = VisualTask(1, 
                PointEmphasisTask(
                    obj.whole_part.start, 
                    [1, 0, 0] | units.kpc,
                    [0, 1, 0] | units.kpc
                ),
                draw_params = DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'o', markersize = 5
                )
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_velocity_tasks(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(3, 
                VelocityScatterTask(
                    [1, 0, 0] | units.kms,
                    [0, 1, 0] | units.kms
                ), 
                obj.whole_part,
                DrawParameters(
                    markersize = 0.02, 
                    channel = obj.color,
                    is_density_plot = True, 
                    resolution = 700,
                    extent = (-400, 400, -400, 400)
                )
            )

            tasks.append(curr)

        self.add_tasks(*tasks)

    def add_distance_task(self):
        curr = VisualTask(4, 
            DistanceTask(
                self.objects[0].whole_part.start, 
                self.objects[1].whole_part.start
            ),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'r'
            )   
        )

        self.add_tasks(curr)

    def add_velocity_profile_task(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(5, 
                VelocityProfileTask(), obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'None', label = obj.name
                )
            )

            tasks.append(curr)

        curr = VisualTask(5, 
            VelocityProfileTask(),
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        self.add_tasks(*tasks, curr)

    def add_mass_profile_task(self):
        tasks = []

        for obj in self.objects:
            curr = VisualTask(6, 
                MassProfileTask(), 
                obj.whole_part,
                DrawParameters(
                    linestyle = 'solid', color = obj.color, 
                    marker = 'None', label = obj.name
                )
            )

            tasks.append(curr)

        curr = VisualTask(6, 
            MassProfileTask(), 
            draw_params = DrawParameters(
                linestyle = 'solid', color = 'y', 
                marker = 'None', label = 'all'
            )
        )

        self.add_tasks(*tasks, curr)

