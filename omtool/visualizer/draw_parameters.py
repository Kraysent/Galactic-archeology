from dataclasses import dataclass
from typing import Optional


@dataclass
class DrawParameters:
    id: str
    markersize: float = 0.1
    linestyle: str = "None"
    color: str = "b"
    marker: str = "o"
    is_density_plot: bool = False
    resolution: int = 100
    extent: tuple[int, int, int, int] = (0, 100, 0, 100)
    label: Optional[str] = None
    channel: str = "b"
    x: str = "x"
    y: str = "y"
    weights: Optional[str] = None
