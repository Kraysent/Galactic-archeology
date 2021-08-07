from typing import Any, Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from utils.plot_parameters import DrawParameters, PlotParameters


class Visualizer:
    def __init__(self, style: str = 'ggplot'):
        plt.style.use(style)
        self.figure = plt.figure()

    @property
    def number_of_axes(self):
        return len(self.figure.axes)

    def add_axes(self, left: float, bottom: float, width: float, height: float):
        self.figure.add_axes([left, bottom, width, height])

    def get_axes(self, axes_id: int = None) -> Axes:
        if axes_id is None:
            return self.figure.axes
        else:
            return self.figure.axes[axes_id]

    def _do_for_all_axes(self, action: Callable[[Axes], Any]):
        results = []

        for ax in self.get_axes():
            results.append(action(ax))

        return results

    def set_plot_parameters(self, axes_id: int, **kwargs):
        params = PlotParameters()

        for (key, value) in kwargs.items():
            setattr(params, key, value)

        axes = self.get_axes(axes_id)

        axes.grid(params.grid)

        axes.set_xlim(params.xlim)
        axes.set_ylim(params.ylim)

        axes.set_xlabel(params.xlabel)
        axes.set_ylabel(params.ylabel)

        if params.xticks is not None:
            axes.set_xticks(params.xticks)
        if params.yticks is not None:
            axes.set_yticks(params.yticks)

        axes.set_title(params.title)
        axes.tick_params(axis = 'x', direction = params.ticks_direction)
        axes.tick_params(axis = 'y', direction = params.ticks_direction)

    def scatter_points(self, 
        axes_id: int, 
        data: Tuple[np.ndarray, np.ndarray], 
        params: DrawParameters
    ):
        axes = self.get_axes(axes_id)
        (x, y) = data

        axes.plot(x, y,
            marker = params.marker, color = params.color,
            markersize = params.markersize, linestyle = params.linestyle
        )

    def plot_image(self, 
        axes_id: int, 
        data: np.ndarray, 
        params: DrawParameters
    ):
        axes = self.get_axes(axes_id)
        axes.imshow(data, 
            extent = params.extent, 
            cmap = params.cmap, 
            norm = params.cmapnorm
        )

    def set_title(self, title: str):
        self.figure.suptitle(title)

    def set_figsize(self, width: float, height: float):
        self.figure.set_size_inches(width, height)

    def save(self, filename: str, dpi: int = 120):
        self.figure.savefig(filename, dpi = dpi, bbox_inches='tight')

        def delete_all(axes: Axes):
            while axes.artists != []:
                axes.artists[0].remove()

            while axes.lines != []:
                axes.lines[0].remove()
            
            while axes.images != []:
                axes.images[0].remove()
                
        self._do_for_all_axes(delete_all)

    def show(self):
        plt.show()
