from typing import Tuple, Union


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
    markersize: float = 0.1
    linestyle: str = 'None'
    color: str = 'b'
    marker: str = 'o'
    blocks: Tuple[Tuple[int, int], ...] = None
    blocks_color: Union[Tuple[str, ...], str] = 'r'
    emph: Tuple[int, int] = (0, 0)
    emph_color = 'r'