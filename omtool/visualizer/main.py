import os
import pathlib
import random
import time
from glob import glob
from typing import Any, Optional

import numpy as np
from PyPDF2 import PdfMerger

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

        if config.pic_filename is not None:
            self.pic_filename_template = str(pathlib.Path(config.output_dir, config.pic_filename))

        if config.pickle_filename is not None:
            self.pickle_filename_template = str(
                pathlib.Path(config.output_dir, config.pickle_filename)
            )

        if config.pdf_name is not None:
            self.pdf_path = str(pathlib.Path(config.output_dir, config.pdf_name))
            self.pdf_tmp_path = str(
                pathlib.Path(
                    config.output_dir, "_".join([str(random.randint(1, 1000)), "tmp", "{}.pdf"])
                )
            )
            self.pdf_object = PdfMerger()

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

        save_args: dict[str, Any] = {}

        if hasattr(self, "pic_filename_template"):
            save_args["pic_filename"] = self.pic_filename_template.format(**iteration_dict)

        if hasattr(self, "pickle_filename_template"):
            save_args["pickle_filename"] = self.pickle_filename_template.format(**iteration_dict)

        if hasattr(self, "pdf_object"):
            save_args["pdf_object"] = self.pdf_object
            save_args["pdf_tmp_path"] = self.pdf_tmp_path.format(int(time.time()))

        self.visualizer.save(**save_args)

    def close(self):
        if hasattr(self, "pdf_object"):
            self.pdf_object.write(self.pdf_path)
            self.pdf_object.close()

            for file in glob(self.pdf_tmp_path.format("*")):
                os.remove(file)
