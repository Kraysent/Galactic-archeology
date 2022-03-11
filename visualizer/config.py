from dataclasses import dataclass
from typing import List, Tuple


def required_get(data: dict, field: str):
    try:
        return data[field]
    except KeyError as e:
        raise Exception(f'No required key {field} found in visualizer configuration.') from e

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

class PanelConfig:
    id: str
    coords: Tuple[int, int, int, int]
    params: PlotParameters

    @staticmethod
    def from_dict(data: dict) -> 'PanelConfig':
        res = PanelConfig()
        res.id = required_get(data, 'id')
        res.coords = tuple(data.get('coords', [0, 1, 1, 1]))
        res.params = PlotParameters(**required_get(data, 'params'))

        return res

class Config:
    plot_interval: slice
    output_dir: str
    title: str
    figsize: Tuple[int, int]
    pic_filename: str
    panels: List[PanelConfig]

    @staticmethod
    def from_dict(data: dict) -> 'Config':
        res = Config()
        res.plot_interval = slice(*data.get('plot_interval', [0, None, 1]))
        res.output_dir = required_get(data, 'output_dir')
        res.title = data.get('title', '')
        res.figsize = tuple(data.get('figsize', [16, 9]))
        res.pic_filename = data.get('pic_filename', 'img-{i:03d}.png')
        res.panels = [
            PanelConfig.from_dict(panel) for panel in required_get(data, 'panels')
        ]

        return res