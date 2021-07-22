from typing import Tuple, Union
import numpy as np

class PlotParameters:
    def __init__(self, **kwargs):
        for (key, val) in kwargs.items():
            setattr(self, key, val)

    grid: bool = False
    xlim: Tuple[int, int] = (None, None)
    ylim: Tuple[int, int] = (None, None)
    xlabel: str = ''
    ylabel: str = ''
    xticks: list = None
    yticks: list = None
    title: str = ''
    ticks_direction: str = 'in'

class DrawParameters:
    def __init__(self, **kwargs):
        for (key, val) in kwargs.items():
            setattr(self, key, val)
            
    markersize: float = 0.1
    linestyle: str = 'None'
    color: str = 'b'
    marker: str = 'o'
    blocks_color: Union[Tuple[str, ...], str] = 'r'
    emph: Tuple[int, int] = (0, 0)
    emph_color = 'r'
    extent: list = [0, 100, 0, 100],
    cmap: str = 'ocean_r'