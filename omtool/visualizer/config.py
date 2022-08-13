from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class PlotParameters:
    grid: bool = False
    xlim: Tuple[Optional[float], Optional[float]] = (None, None)
    ylim: Tuple[Optional[float], Optional[float]] = (None, None)
    xlabel: str = ""
    ylabel: str = ""
    xticks: Optional[list] = None
    yticks: Optional[list] = None
    title: str = ""
    ticks_direction: str = "in"
    xscale = "linear"
    basex = 10
    yscale = "linear"
    basey = 10


@dataclass
class PanelConfig:
    id: str
    coords: Tuple[float, ...]
    params: PlotParameters


@dataclass
class VisualizerConfig:
    output_dir: str
    title: str
    figsize: Tuple[int, ...]
    pic_filename: str
    pickle_filename: Optional[str]
    panels: List[PanelConfig]
