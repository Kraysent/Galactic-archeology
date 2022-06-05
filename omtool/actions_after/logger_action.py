from typing import Optional, Tuple

import numpy as np

import omtool.json_logger as logger


def logger_action(
    data: Tuple[np.ndarray, np.ndarray], id: str = "msg", print_last: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Handler that logs ndarrays to the INFO level.
    """
    payload = {}

    if print_last:
        payload["x"] = data[0].tolist()[-1]
        payload["y"] = data[1].tolist()[-1]
    else:
        payload["x"] = data[0].tolist()
        payload["y"] = data[1].tolist()

    logger.info(message_type=id, payload=payload)

    return data
