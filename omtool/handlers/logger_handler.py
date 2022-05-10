from typing import Tuple

import numpy as np

import omtool.json_logger as logger


def logger_handler(data: Tuple[np.ndarray, np.ndarray], parameters: dict = None):
    """
    Handler that logs ndarrays to the INFO level.
    """
    if parameters is None:
        parameters = {}

    if parameters["print_last"]:
        logger.info(
            message_type=parameters["id"],
            payload={"x": data[0].tolist()[-1], "y": data[1].tolist()[-1]},
        )
    else:
        logger.info(
            message_type=parameters["id"],
            payload={"x": data[0].tolist(), "y": data[1].tolist()},
        )
