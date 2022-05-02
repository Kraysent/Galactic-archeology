'''
Module that describes all of the tasks.
'''
from omtool.core.analysis.tasks.abstract_task import *
from omtool.core.analysis.tasks.bound_mass_task import BoundMassTask
from omtool.core.analysis.tasks.density_profile_task import DensityProfileTask
from omtool.core.analysis.tasks.distance_task import DistanceTask
from omtool.core.analysis.tasks.eccentricity_task import EccentricityTask
from omtool.core.analysis.tasks.mass_profile_task import MassProfileTask
from omtool.core.analysis.tasks.potential_task import PotentialTask
from omtool.core.analysis.tasks.scatter_task import ScatterTask
from omtool.core.analysis.tasks.time_evolution_task import TimeEvolutionTask
from omtool.core.analysis.tasks.velocity_profile_task import VelocityProfileTask


def get_task(task_name: str, args: dict) -> AbstractTask:
    '''
    Creates instance of the specific task with arguments that were provided in args dict.
    '''
    task_map = {
        'ScatterTask': ScatterTask,
        'TimeEvolutionTask': TimeEvolutionTask,
        'DistanceTask': DistanceTask,
        'VelocityProfileTask': VelocityProfileTask,
        'MassProfileTask': MassProfileTask,
        'DensityProfileTask': DensityProfileTask,
        'EccentricityTask': EccentricityTask,
        'PotentialTask': PotentialTask,
        'BoundMassTask': BoundMassTask
    }

    return task_map[task_name](**args)
