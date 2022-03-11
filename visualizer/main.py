from typing import Tuple

import numpy as np

from visualizer.config import Config
from visualizer.draw_parameters import DrawParameters
from visualizer.visualizer import Visualizer


class VisualizerService:
    def __init__(self, config: Config):
        self.visualizer = Visualizer()
        self.visualizer.set_figsize(*config.figsize)
        self.title_template = config.title
        self.pic_filename_template = f'{config.output_dir}/{config.pic_filename}'
        
        for panel in config.panels:
            self.visualizer.add_axes(panel)

    def run_handler(self, data: Tuple[np.ndarray, np.ndarray], parameters: dict):
        draw_parameters = DrawParameters(**parameters)
        self.visualizer.plot(data, draw_parameters)

    def save(self, iteration_dict: dict):
        self.visualizer.set_title(self.title_template.format(**iteration_dict))
        self.visualizer.save(self.pic_filename_template.format(**iteration_dict))
        