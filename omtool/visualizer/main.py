from typing import Tuple

import numpy as np

from omtool.visualizer.config import Config
from omtool.visualizer.draw_parameters import DrawParameters
from omtool.visualizer.visualizer import Visualizer


class VisualizerService:
    '''
    Service that is responsible for saving images.
    '''

    def __init__(self, config: Config):
        self.visualizer = Visualizer()
        self.visualizer.set_figsize(*config.figsize)
        self.title_template = config.title
        self.pic_filename_template = f'{config.output_dir}/{config.pic_filename}'

        for panel in config.panels:
            self.visualizer.add_axes(panel)

    def plot(self, data: Tuple[np.ndarray, np.ndarray], parameters: dict):
        '''
        Add data to plot specified in parameters.
        '''
        draw_parameters = DrawParameters(**parameters)
        self.visualizer.plot(data, draw_parameters)

    def save(self, iteration_dict: dict):
        '''
        Save current plot to file from config.
        '''
        self.visualizer.set_title(self.title_template.format(**iteration_dict))
        self.visualizer.save(
            self.pic_filename_template.format(**iteration_dict))
