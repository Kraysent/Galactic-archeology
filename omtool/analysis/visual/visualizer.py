from typing import Any, Callable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from omtool.analysis.config import DrawParameters, PlotParameters
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

    @staticmethod
    def _scale_array(array: np.ndarray, start: float, end: float) -> np.ndarray:
        max_val = array.max()
        min_val = array.min()
        span = max_val - min_val

        if span != 0:
            diff = array - min_val
            non_zero_filter = diff != 0
            array[non_zero_filter] = (1 - diff[non_zero_filter] / span) * (end - start) + start

        return array

    @staticmethod
    def _set_background_color(array: np.ndarray, color: float) -> np.ndarray:
        mask = (array[:, :] ** 2).sum(axis = 2) == 0
        array[:, :][mask] = color

        return array

    def _draw_images(self, lst: List[Tuple[int, dict]], params: List[DrawParameters], background_color = 1):
        for (axes_id, channels) in lst:
            for i in ('r', 'g', 'b'):
                channels[i] = Visualizer._scale_array(channels[i], 0, 1)

            rgb_map = np.stack((channels['r'], channels['g'], channels['b']), 2)
            rgb_map = self._set_background_color(rgb_map, background_color)

            self.get_axes(axes_id).imshow(
                rgb_map,
                extent = params[axes_id].extent
            )

    def _get_hist(self, 
        x1: np.ndarray, 
        x2: np.ndarray, 
        resolution: int, 
        extent: Tuple[float, float, float, float]
    ) -> np.ndarray:
        hist, _, _ = np.histogram2d(x1, x2, resolution, range = [
            extent[:2], extent[2:]
        ])
        hist = np.flip(hist.T, axis = 0)

        return hist

    def set_title(self, title: str):
        self.figure.suptitle(title)

    def set_figsize(self, width: float, height: float):
        self.figure.set_size_inches(width, height)

    def save(self, filename: str, dpi: int = 120):
        images = {}
        imparams = {}

        for (axes_id, data, params) in self.pictures:
            if not params.is_density_plot:
                self._scatter_points(axes_id, data, params)
            else:
                hist = self._get_hist(data[0], data[1], params.resolution, params.extent)

                if not (axes_id in images.keys()):
                    images[axes_id] = {
                        'r': np.zeros(hist.shape),
                        'g': np.zeros(hist.shape),
                        'b': np.zeros(hist.shape)
                    }

                images[axes_id][params.channel] += hist    
                imparams[axes_id] = params

        self._draw_images(images.items(), imparams, 0.85)

        self.figure.savefig(filename, dpi = dpi, bbox_inches='tight')

        def delete_all(axes: Axes):
            while len(axes.artists) != 0:
                axes.artists[0].remove()

            while len(axes.lines) != 0:
                axes.lines[0].remove()
            
            while len(axes.images) != 0:
                axes.images[0].remove()
                
        self.pictures.clear()
        self._do_for_all_axes(delete_all)

    def show(self):
        plt.show()
