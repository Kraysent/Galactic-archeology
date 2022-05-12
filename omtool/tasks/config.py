from omtool.core.datamodel import AbstractTask
from omtool.core.utils import required_get
from omtool.tasks.get_task import get_task


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
