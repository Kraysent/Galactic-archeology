import pathlib
from typing import Any, Optional

import numpy as np

from omtool.visualizer.config import VisualizerConfig
from omtool.visualizer.draw_parameters import DrawParameters
from omtool.visualizer.visualizer import Visualizer


class VisualizerService:
    """
    Service that is responsible for saving images.
    """

    def __init__(self, config: VisualizerConfig):
        self.visualizer = Visualizer()
        self.visualizer.set_figsize(*config.figsize)
        self.title_template = config.title
        pathlib.Path(config.output_dir).mkdir(parents=False, exist_ok=True)
        self.pic_filename_template = str(pathlib.Path(config.output_dir, config.pic_filename))
        if config.pickle_filename is not None:
            self.pickle_filename_template = str(
                pathlib.Path(config.output_dir, config.pickle_filename)
            )

        for panel in config.panels:
            self.visualizer.add_axes(panel)

    def plot(self, data: dict[str, np.ndarray], parameters: Optional[dict] = None):
        """
        Add data to plot specified in parameters.
        """
        parameters = parameters or {}

        draw_parameters = DrawParameters(**parameters)
        self.visualizer.plot(data, draw_parameters)

    def save(self, iteration_dict: dict):
        """
        Save current plot to file from config.
        """
        self.visualizer.set_title(self.title_template.format(**iteration_dict))

        save_args: list[Any] = [self.pic_filename_template.format(**iteration_dict)]

        if hasattr(self, "pickle_filename_template"):
            save_args.append(self.pickle_filename_template.format(**iteration_dict))

        self.visualizer.save(*save_args)
