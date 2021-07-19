from typing import Tuple


class PlotParameters:
    def __init__(self, axes_id: int, **kwargs):
        self._axes_id = axes_id

        for (key, val) in kwargs.items():
            setattr(self, key, val)

    @property
    def axes_id(self) -> int:
        return self._axes_id 

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
    emph: Tuple[int, int] = (0, 0)
    emph_color = 'r'