from typing import Any, Callable, Tuple
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import matplotlib.gridspec as gridspec
import numpy as np
from utils.plot_parameters import PlotParameters, DrawParameters

class Visualizer:
    def __init__(self):
        self._axes = []

    def setup_grid(self, hratio: float):
        self._left_gs = gridspec.GridSpec(2, 2)
        self._right_gs = gridspec.GridSpec(2, 1)
        ax1 = self._figure.add_subplot(self._left_gs[:, 0])
        ax2 = self._figure.add_subplot(self._left_gs[:, 1])
        ax3 = self._figure.add_subplot(self._right_gs[0, :])
        ax4 = self._figure.add_subplot(self._right_gs[1, :])
        self._left_gs.update(right = hratio / (hratio + 1))
        self._right_gs.update(left = hratio / (hratio + 1) + 0.05)
        self._left_gs.update(wspace = 0)

        self._axes.append(ax1)
        self._axes.append(ax2)
        self._axes.append(ax3)
        self._axes.append(ax4)

    def add_subplot(self, row_span: Tuple[int, int], col_span: Tuple[int, int]):
        self._axes.append(plt.subplot(self._gridspec[col_span[0]: col_span[1], row_span[0]: row_span[1]]))

    @property
    def _figure(self) -> Figure:
        return plt.gcf()

    def _do_for_all_axes(self, action: Callable[[Axes], Any]):
        results = []

        for ax in self._axes:
            results.append(action(ax))

        return results

    def set_plot_parameters(self, axes_id: int, params: PlotParameters):
        axes: Axes = self._axes[axes_id]

        axes.grid(params.grid)

        if all(params.xlim):
            axes.set_xlim(params.xlim)

        if all(params.ylim):
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

    def plot_points(
        self, axes_id: int, x: np.ndarray, y: np.ndarray, params: DrawParameters,
        blocks: Tuple[Tuple[int, int], ...]
    ):
        axes = self._axes[axes_id]

        for i in range(len(blocks)):
            (start, end) = blocks[i]

            axes.plot(x[start: end], y[start: end],
                marker = params.marker, color = params.blocks_color[i],
                markersize = params.markersize, linestyle = params.linestyle
            )

    def set_title(self, title: str):
        self._figure.suptitle(title)

    def set_figsize(self, width: float, height: float):
        self._figure.set_size_inches(width, height)

    def save(self, filename: str, dpi: int = 120):
        self._figure.savefig(filename, dpi = dpi, bbox_inches='tight')

        self._do_for_all_axes(lambda axes: axes.cla())
