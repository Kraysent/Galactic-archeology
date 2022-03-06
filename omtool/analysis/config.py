from dataclasses import dataclass
from typing import Any, Tuple

import io_service
import matplotlib as mpl
import yaml
from omtool.analysis.tasks import get_task
from omtool.datamodel import required_get, yaml_loader


@dataclass
class PlotParameters:
    grid: bool = False
    xlim: Tuple[int, int] = (None, None)
    ylim: Tuple[int, int] = (None, None)
    xlabel: str = ''
    ylabel: str = ''
    xticks: list = None
    yticks: list = None
    title: str = ''
    ticks_direction: str = 'in'
    xscale = 'linear'
    basex = 10
    yscale = 'linear'
    basey = 10

@dataclass
class DrawParameters:  
    markersize: float = 0.1
    linestyle: str = 'None'
    color: str = 'b'
    marker: str = 'o'
    is_density_plot: bool = False
    resolution: int = 100
    extent: Tuple[int, int, int, int] = (0, 100, 0, 100)
    cmap: str = 'ocean_r'
    cmapnorm: Any = mpl.colors.LogNorm()
    label: str = None
    channel: str = 'b'

class Task:
    @staticmethod
    def from_dict(input: dict) -> 'Task':
        res = Task()
        res.slice = slice(*input.get('slice', [0, None, 1]))
        res.abstract_task = None
        res.display = DrawParameters(**input.get('display', { }))
        res.abstract_task = get_task(
            required_get(input, 'name'), 
            input.get('args', { })
        )

        return res

class Plot:
    @staticmethod
    def from_dict(input: dict) -> 'Plot':
        res = Plot()
        res.coords = tuple(input.get('coords', [0, 1, 1, 1]))
        res.params = input.get('params', {
            'xlim': [0, 1],
            'ylim': [0, 1]
        })
        res.tasks = [
            Task.from_dict(task) for task in input.get('tasks', [])
        ]

        return res

class AnalysisConfig:
    @staticmethod
    def from_yaml(filename: str) -> 'AnalysisConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())
        
        return AnalysisConfig.from_dict(data)

    @staticmethod
    def from_dict(input: dict) -> 'AnalysisConfig':
        res = AnalysisConfig()
        res.figsize = tuple(input.get('figsize', [20, 11]))
        res.plot_interval_slice = slice(*input.get('plot_interval', [0, None, 1]))
        res.plots = [
            Plot.from_dict(plot) for plot in required_get(input, 'plots')
        ]
        res.output_dir = required_get(input, 'output_dir')
        res.title = input.get('title', 'Time {time} Myr')
        res.input_file = io_service.Config.from_dict(required_get(input, 'input_file'))
        res.pic_filename = input.get('pic_filename', 'img-{i:03d}.png')

        return res

