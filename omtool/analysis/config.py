from typing import Any, Dict, List, Tuple
import yaml
from omtool.analysis.tasks import get_task
from omtool.analysis.tasks.abstract_task import AbstractTask
from omtool.analysis.visual.plot_parameters import DrawParameters
from omtool.datamodel import yaml_loader

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

class Task:
    _args: Dict[str, Any]
    _name: str
    _display_args: dict

    slice: slice
    abstract_task: AbstractTask

    def from_dict(input: dict) -> 'Task':
        res = Task()
        res._args = { }
        res._name = ''
        res._display_args = { }
        res.slice = slice(0, None)
        res.abstract_task = None

        if 'args' in input:
            res._args = input['args']

        if 'slice' in input:
            res.slice = slice(*input['slice'])

        if 'display' in input:
            for key, val in input['display'].items():
                res._display_args[key] = val

        res.display = DrawParameters(**res._display_args)

        if 'name' in input:
            res._name = input['name']

            res.abstract_task = get_task(res._name, res._args)
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
    # optional parameters
    figsize: Tuple[int, int]
    plot_interval: int

    # required parameters
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
        res.plot_interval = 1
        res.plots = []
        res.output_dir = ''
        res.input_file = InputFile()

        if 'figsize' in data:
            res.figsize = tuple(data['figsize'])

        if 'plot_interval' in data:
            res.plot_interval = int(data['plot_interval'])

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

