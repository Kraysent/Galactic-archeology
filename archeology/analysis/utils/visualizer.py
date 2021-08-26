from typing import Any, Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
from archeology.analysis.utils import DrawParameters, PlotParameters
from matplotlib.axes import Axes


class Visualizer:
    def __init__(self, style: str = 'ggplot'):
        plt.style.use(style)
        self.figure = plt.figure()
        self.pictures = []

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

        if params.xscale == 'log':
            axes.set_xscale(params.xscale, base = params.basex)
        else: 
            axes.set_xscale(params.xscale)

        if params.yscale == 'log':
            axes.set_yscale(params.yscale, base = params.basey)
        else:
            axes.set_yscale(params.yscale)

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

    def plot(self, axes_id: int, data, params: DrawParameters):
        self.pictures.append((axes_id, data, params))

    def _scatter_points(self, 
        axes_id: int, 
        data: Tuple[np.ndarray, np.ndarray], 
        params: DrawParameters
    ):
        axes = self.get_axes(axes_id)
        (x, y) = data

        if params.label is None:
            axes.plot(x, y,
                marker = params.marker, color = params.color,
                markersize = params.markersize, linestyle = params.linestyle
            )
        else:
            axes.plot(x, y,
                marker = params.marker, color = params.color,
                markersize = params.markersize, linestyle = params.linestyle,
                label = params.label
            )
            axes.legend()

    def _plot_image(self, 
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
        images = {}
        imparams = {}

        for (axes_id, data, params) in self.pictures:
            if type(data) is tuple:
                self._scatter_points(axes_id, data, params)
            else:
                if not (axes_id in images.keys()):
                    images[axes_id] = {}

                for i in ('r', 'g', 'b'):
                    if not i in images[axes_id].keys():
                        images[axes_id][i] = np.zeros(data.shape)

                images[axes_id][params.channel] += data    
                imparams[axes_id] = params
                # self._plot_image(axes_id, data, params)

        for (axes_id, channels) in images.items():
            for i in ('r', 'g', 'b'):
                if channels[i].max() - channels[i].min() != 0:
                    span = channels[i].max() - channels[i].min()
                    diff = channels[i] - channels[i].min()
                    channels[i] = diff / span

            stack = np.stack((channels['r'], channels['g'], channels['b']), 2)
            mask = (stack[:, :, 0] ** 2 + stack[:, :, 1] ** 2 + stack[:, :, 2] ** 2) == 0
            stack[:, :, 0][mask] = 0.85
            stack[:, :, 1][mask] = 0.85
            stack[:, :, 2][mask] = 0.85

            self.get_axes(axes_id).imshow(
                stack,
                extent = imparams[axes_id].extent
            )
            

        self.figure.savefig(filename, dpi = dpi, bbox_inches='tight')

        self.pictures.clear()

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
