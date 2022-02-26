from omtool.analysis.tasks.abstract_task import *
from omtool.analysis.tasks.bound_mass_task import BoundMassTask
from omtool.analysis.tasks.distance_task import DistanceTask
from omtool.analysis.tasks.eccentricity_task import EccentricityTask
from omtool.analysis.tasks.mass_profile_task import MassProfileTask
from omtool.analysis.tasks.potential_task import PotentialTask
from omtool.analysis.tasks.scatter_task import ScatterTask
from omtool.analysis.tasks.time_evolution_task import TimeEvolutionTask
from omtool.analysis.tasks.velocity_profile_task import VelocityProfileTask


def get_task(task_name: str, args: dict) -> AbstractTask:
    task_map = {
        'ScatterTask': ScatterTask,
        'TimeEvolutionTask': TimeEvolutionTask,
        'DistanceTask': DistanceTask,
        'VelocityProfileTask': VelocityProfileTask,
        'MassProfileTask': MassProfileTask,
        'EccentricityTask': EccentricityTask,
        'PotentialTask': PotentialTask,
        'BoundMassTask': BoundMassTask
    }

    return task_map[task_name](**args)
