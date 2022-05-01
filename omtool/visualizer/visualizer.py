from typing import Any, Callable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from omtool.visualizer.config import PanelConfig
from omtool.visualizer.draw_parameters import DrawParameters


class Visualizer:
    def __init__(self, style: str = 'ggplot'):
        plt.style.use(style)
        self.figure = plt.figure()
        self.pictures = []
        self.axes_ids = { }

    @property
    def number_of_axes(self):
        return len(self.figure.axes)

    def set_title(self, title: str):
        self.figure.suptitle(title)

    def set_figsize(self, width: float, height: float):
        self.figure.set_size_inches(width, height)

    def add_axes(self, panel_config: PanelConfig):
        self.figure.add_axes(panel_config.coords)
        self.axes_ids[panel_config.id] = len(self.figure.axes) - 1

        # need to refactor this, axes can be obtained directly from add_axes method
        params = panel_config.params
        axes = self.get_axes(panel_config.id)

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

    def get_axes(self, id: str = None) -> Axes:
        if id is None:
            return self.figure.axes
        else:
            return self.figure.axes[self.axes_ids[id]]

    def _do_for_all_axes(self, action: Callable[[Axes], Any]):
        results = []

        for ax in self.get_axes():
            results.append(action(ax))

        return results

    def plot(self, data, params: DrawParameters):
        self.pictures.append((data, params))

    def _scatter_points(self, 
        data: Tuple[np.ndarray, np.ndarray], 
        params: DrawParameters
    ):
        axes = self.get_axes(params.id)
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

    def _scale_array(self, array: np.ndarray, start: float, end: float) -> np.ndarray:
        max_val = array.max()
        min_val = array.min()
        span = max_val - min_val

        if span != 0:
            diff = array - min_val
            non_zero_filter = diff != 0
            array[non_zero_filter] = (1 - diff[non_zero_filter] / span) * (end - start) + start

        return array

    def _set_background_color(self, array: np.ndarray, color: float) -> np.ndarray:
        mask = (array[:, :] ** 2).sum(axis = 2) == 0
        array[:, :][mask] = color

        return array

    def _draw_images(self, lst: List[Tuple[int, dict]], params: List[DrawParameters], background_color = 1):
        for (axes_id, channels) in lst:
            for i in ('r', 'g', 'b'):
                channels[i] = self._scale_array(channels[i], 0, 1)

            rgb_map = np.stack((channels['r'], channels['g'], channels['b']), 2)
            rgb_map = self._set_background_color(rgb_map, background_color)

            self.get_axes(axes_id).imshow(
                rgb_map,
                extent = params[axes_id].extent, interpolation='nearest', aspect='auto'
            )

    def save(self, filename: str, dpi: int = 120):
        images = {}
        imparams = {}

        for (data, params) in self.pictures:
            if not params.is_density_plot:
                self._scatter_points(data, params)
            else:
                hist = self._get_hist(data[0], data[1], params.resolution, params.extent)

                if not (params.id in images.keys()):
                    images[params.id] = {
                        'r': np.zeros(hist.shape),
                        'g': np.zeros(hist.shape),
                        'b': np.zeros(hist.shape)
                    }

                images[params.id][params.channel] += hist    
                imparams[params.id] = params

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
