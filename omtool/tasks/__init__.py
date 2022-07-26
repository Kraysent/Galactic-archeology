"""
Module that describes all of the tasks.
"""
from omtool.tasks.bound_mass_task import BoundMassTask
from omtool.tasks.config import TasksConfig, TasksConfigSchema, initialize_tasks
from omtool.tasks.density_profile_task import DensityProfileTask
from omtool.tasks.distance_task import DistanceTask
from omtool.tasks.mass_profile_task import MassProfileTask
from omtool.tasks.potential_task import PotentialTask
from omtool.tasks.scatter_task import ScatterTask
from omtool.tasks.time_evolution_task import TimeEvolutionTask
from omtool.tasks.velocity_profile_task import VelocityProfileTask
