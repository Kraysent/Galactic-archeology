from dataclasses import dataclass
from typing import Any

from amuse.lab import ScalarQuantity
from zlog import Field, logger

from omtool.core.tasks import DataType


@dataclass
class ScalarQuantityField(Field):
    def __init__(self, value: ScalarQuantity, unit) -> None:
        self.value = value
        self.unit = unit
        super().__init__()

    def log(self) -> dict[str, Any]:
        return {"value": self.value.value_in(self.unit), "unit": str(self.unit)}


def logger_action(
    data: DataType, id: str = "msg", print_last: bool = False, fields: list = None
) -> DataType:
    """
    Handler that logs fields to the INFO level.
    """
    fields = fields or []
    event = logger.info().string("id", id)

    if fields == []:
        fields = list(data.keys())

    for field in fields:
        value = data[field]

        # TODO: need to refactor this!
        if isinstance(value, ScalarQuantity):
            event = event.field(field, ScalarQuantityField(value, value.unit))
        elif print_last:
            event = event.float(field, value[-1])
        else:
            event = event.dict(field, value)

    event.send()

    return data
