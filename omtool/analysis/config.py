from dataclasses import dataclass
import string
from typing import Any, Dict, List, Tuple

import matplotlib as mpl
import yaml
from omtool.analysis.tasks import get_task
from omtool.analysis.tasks.abstract_task import AbstractTask
from omtool.datamodel import yaml_loader


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

class InputFile:
    # optional parameters
    format: str

    # required parameters
    filenames: List[str]

    @staticmethod
    def from_dict(input: dict) -> 'InputFile':
        res = InputFile()
        res.format = 'fits'
        res.filenames = []

        if 'format' in input:
            res.format = input['format']   

        if 'filenames' in input:
            res.filenames = list(input['filenames']) 
        else:
            raise Exception("No input filenames specified in analysis configuration file")

        return res

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
    slice: slice
    abstract_task: AbstractTask
    display: DrawParameters

    def from_dict(input: dict) -> 'Task':
        res = Task()
        res.slice = slice(0, None)
        res.abstract_task = None

        args = { }
        name = ''
        display_args = { }

        if 'args' in input:
            args = input['args']

        if 'slice' in input:
            res.slice = slice(*input['slice'])

        if 'display' in input:
            for key, val in input['display'].items():
                display_args[key] = val

        res.display = DrawParameters(**display_args)

        if 'name' in input:
            name = input['name']

            res.abstract_task = get_task(name, args)
        else: 
            raise Exception("No task name specified in analysis configuration file")

        return res

class Plot:
    coords: Tuple[int, int, int, int]
    params: Dict[str, Any]
    tasks: List[Task]

    @staticmethod
    def from_dict(input: dict) -> 'Plot':
        res = Plot()
        res.coords = (0, 0, 1, 1)
        res.params = {
            'xlim': [0, 1],
            'ylim': [0, 1]
        }
        res.tasks = []

        if 'coords' in input:
            res.coords = tuple(input['coords'])
        
        if 'params' in input:
            for key, val in input['params'].items():
                res.params[key] = val

        if 'tasks' in input:
            for task in input['tasks']:
                res.tasks.append(Task.from_dict(task))

        return res

class AnalysisConfig:
    figsize: Tuple[int, int]
    plot_interval_slice: int
    title: string
    plots: List[Plot]
    output_dir: str
    input_file: InputFile

    @staticmethod
    def from_yaml(filename: str) -> 'AnalysisConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        res = AnalysisConfig()
        res.figsize = (20, 11)
        res.plot_interval_slice = slice(0, None)
        res.plots = []
        res.output_dir = ''
        res.title = 'Time {time} Myr'
        res.input_file = InputFile()
        res.pic_filename = 'img-{i:03d}.png'

        if 'figsize' in data:
            res.figsize = tuple(data['figsize'])

        if 'plot_interval' in data:
            res.plot_interval_slice = slice(*data['plot_interval'])

        if 'pic_filename' in data:
            res.pic_filename = data['pic_filename']

        if 'title' in data:
            res.title = data['title']

        if 'output_dir' in data:
            res.output_dir = data['output_dir']
        else: 
            raise Exception("No output directory specified in analysis configuration file")
        
        if 'input_file' in data:
            res.input_file = InputFile.from_dict(data['input_file'])
        else: 
            raise Exception("No input file specified in analysis configuration file")

        if 'plots' in data:
            for plot in data['plots']:
                res.plots.append(Plot.from_dict(plot))
        else: 
            raise Exception("No plots specified in analysis configuration file")

        return res

