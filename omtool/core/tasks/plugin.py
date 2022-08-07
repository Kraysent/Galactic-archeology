from typing import Type

from zlog import logger

from omtool.core.datamodel import AbstractTask

TASKS = {}


def register_task(name: str):
    if name in TASKS:
        logger.error().string("name", name).msg("name conflict when importing task")
        return

    def wrapper_register_task(task_class: Type[AbstractTask]):
        logger.debug().string("name", name).msg("imported task")
        task = task_class
        TASKS[name] = task
        return task

    return wrapper_register_task
