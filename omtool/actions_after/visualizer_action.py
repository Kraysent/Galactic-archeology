from typing import Optional, Tuple

import numpy as np

from omtool import visualizer


class VisualizerAction:
    def __init__(self, service: visualizer.VisualizerService):
        self.service = service

    def __call__(
        self, data: Tuple[np.ndarray, np.ndarray], parameters: Optional[dict] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        self.service.plot(data, parameters)

        return data
