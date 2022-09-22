from zlog import logger

from omtool.core.tasks import DataType


def logger_action(data: DataType, id: str = "msg", print_last: bool = False) -> DataType:
    """
    Handler that logs ndarrays to the INFO level.
    """
    event = logger.info().string("id", id)

    for key, val in data.items():
        if print_last:
            event = event.float(key, val[-1])
        else:
            event = event.list(key, val.tolist())

    event.send()

    return data
