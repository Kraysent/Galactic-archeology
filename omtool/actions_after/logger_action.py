import numpy as np

import omtool.json_logger as logger


def logger_action(
    data: dict[str, np.ndarray], id: str = "msg", print_last: bool = False
) -> dict[str, np.ndarray]:
    """
    Handler that logs ndarrays to the INFO level.
    """
    payload = {}

    if print_last:
        for key, val in data.items():
            payload[key] = val.tolist()[-1]
    else:
        for key, val in data.items():
            payload[key] = val.tolist()

    logger.info(message_type=id, payload=payload)

    return data
