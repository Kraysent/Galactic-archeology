from dataclasses import dataclass
from typing import Callable

from marshmallow import Schema, fields, post_load
from zlog import logger

from omtool.core.datamodel import AbstractTask, HandlerTask
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


class TasksConfigSchema(Schema):
    name = fields.Raw(required=True, description="Name of the task.")
    actions_before = fields.List(
        fields.Dict(fields.Str()),
        load_default=[],
        description="List of actions that would run some function on a given snapshot "
        "before running the task.",
    )
    actions_after = fields.List(
        fields.Dict(fields.Str()),
        load_default=[],
        description="List of actions that would run some function on every single result "
        "of the task.",
    )
    args = fields.Dict(
        fields.Str(), load_default={}, description="Arguments to the constructor of the task."
    )

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


def initialize_tasks(
    configs: list[Config], actions_before: dict[str, Callable], actions_after: dict[str, Callable]
) -> list[HandlerTask]:
    tasks: list[HandlerTask] = []

    for config in configs:
        curr_task = HandlerTask(config.name)

        for action_params in config.actions_before:
            action_name = action_params.pop("type", None)

            if action_name is None:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if action_name not in actions_before:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def action(snapshot, name=action_name, params=action_params):
                return actions_before[name](snapshot, **params)

            curr_task.actions_before.append(action)

        for handler_params in config.actions_after:
            handler_name = handler_params.pop("type", None)

            if handler_name is None:
                logger.error().msg(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if handler_name not in actions_after:
                logger.error().msg(
                    f"Handler type {handler_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def handler(data, name=handler_name, params=handler_params):
                return actions_after[name](data, **params)

            curr_task.actions_after.append(handler)

        tasks.append(curr_task)
        logger.debug().string("task", type(curr_task.task).__name__).msg("Init")

    return tasks
