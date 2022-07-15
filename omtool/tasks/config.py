from dataclasses import dataclass

from marshmallow import Schema, fields, post_load

from omtool.core.datamodel import AbstractTask
from omtool.tasks.bound_mass_task import BoundMassTask
from omtool.tasks.density_profile_task import DensityProfileTask
from omtool.tasks.distance_task import DistanceTask
from omtool.tasks.mass_profile_task import MassProfileTask
from omtool.tasks.potential_task import PotentialTask
from omtool.tasks.scatter_task import ScatterTask
from omtool.tasks.time_evolution_task import TimeEvolutionTask
from omtool.tasks.velocity_profile_task import VelocityProfileTask


@dataclass
class Config:
    name: AbstractTask
    actions_before: list[dict]
    actions_after: list[dict]


class ConfigSchema(Schema):
    name = fields.Raw(required=True)
    actions_before = fields.List(fields.Dict(fields.Str()), load_default=[])
    actions_after = fields.List(fields.Dict(fields.Str()), load_default=[])
    args = fields.Dict(fields.Str(), load_default={})

    @post_load
    def make(self, data: dict, **kwargs):
        data["name"] = get_task(data["name"], data.pop("args"))
        return Config(**data)


def get_task(task_name: str, args: dict) -> AbstractTask:
    """
    Creates instance of the specific task with arguments that were provided in args dict.
    """
    task_map = {
        "ScatterTask": ScatterTask,
        "TimeEvolutionTask": TimeEvolutionTask,
        "DistanceTask": DistanceTask,
        "VelocityProfileTask": VelocityProfileTask,
        "MassProfileTask": MassProfileTask,
        "DensityProfileTask": DensityProfileTask,
        "PotentialTask": PotentialTask,
        "BoundMassTask": BoundMassTask,
    }

    return task_map[task_name](**args)
