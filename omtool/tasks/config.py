from omtool.tasks.abstract_task import AbstractTask
from omtool.tasks.get_task import get_task
from omtool.core.datamodel import required_get

class Config:
    """
    Configuration for each particular task.
    """

    slice: slice
    abstract_task: AbstractTask
    handlers: dict

    @staticmethod
    def from_dict(data: dict) -> "Config":
        """
        Construct this object from dictionary.
        """
        res = Config()
        res.slice = slice(*data.get("slice", [0, None, 1]))
        res.handlers = data.get("handlers", {})
        res.abstract_task = get_task(required_get(data, "name"), data.get("args", {}))

        return res
