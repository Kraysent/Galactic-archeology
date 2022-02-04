from typing import Tuple


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
    xscale = 'linear'
    basex = 10
    yscale = 'linear'
    basey = 10
