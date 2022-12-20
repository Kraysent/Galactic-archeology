from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from PyPDF2 import PdfMerger

from omtool.visualizer.config import PanelConfig
from omtool.visualizer.draw_parameters import DrawParameters


class Visualizer:
    def __init__(self, style: str = "ggplot"):
        plt.style.use(style)
        self.figure = plt.figure()
        self.pictures: List[tuple[dict[str, np.ndarray], DrawParameters]] = []
        self.axes_ids: Dict[str, int] = {}

    @property
    def number_of_axes(self):
        return len(self.figure.axes)

    def set_title(self, title: str):
        self.figure.suptitle(title)

    def set_figsize(self, width: int, height: int):
        px = 1 / plt.rcParams["figure.dpi"]
        self.figure.set_size_inches(width * px, height * px)

    def add_axes(self, panel_config: PanelConfig):
        axes: Axes = self.figure.add_axes(panel_config.coords)
        self.axes_ids[panel_config.id] = len(self.figure.axes) - 1

        params = panel_config.params

        if params.xscale == "log":
            axes.set_xscale(params.xscale, base=params.basex)
        else:
            axes.set_xscale(params.xscale)

        if params.yscale == "log":
            axes.set_yscale(params.yscale, base=params.basey)
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
        axes.tick_params(axis="x", direction=params.ticks_direction)
        axes.tick_params(axis="y", direction=params.ticks_direction)

    def get_axes(self, id: Optional[str] = None) -> Axes:
        return self.figure.axes if id is None else self.figure.axes[self.axes_ids[id]]

    def _do_for_all_axes(self, action: Callable[[Axes], Any]):
        return [action(ax) for ax in self.get_axes()]

    def plot(self, data: dict[str, np.ndarray], params: DrawParameters):
        self.pictures.append((data, params))

    def _scatter_points(self, data: dict[str, np.ndarray], params: DrawParameters):
        axes = self.get_axes(params.id)
        x = data[params.x]
        y = data[params.y]

        plot_kwargs = {
            "marker": params.marker,
            "color": params.color,
            "markersize": params.markersize,
            "linestyle": params.linestyle,
        }

        if params.label is not None:
            plot_kwargs["label"] = params.label

        axes.plot(x, y, **plot_kwargs)

        if params.label is not None:
            axes.legend()

    def _get_hist(
        self,
        x1: np.ndarray,
        x2: np.ndarray,
        resolution: int,
        extent: Tuple[float, float, float, float],
        weights: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        if weights is None:
            hist, _, _ = np.histogram2d(x1, x2, resolution, range=[extent[:2], extent[2:]])
        else:
            hist, _, _ = np.histogram2d(
                x1, x2, resolution, range=[extent[:2], extent[2:]], weights=weights, normed=True
            )
        hist = np.flip(hist.T, axis=0)

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
        mask = (array[:, :] ** 2).sum(axis=2) == 0
        array[:, :][mask] = color

        return array

    def _draw_images(
        self,
        images: dict[str, dict[str, np.ndarray]],
        params: dict[str, DrawParameters],
        background_color: float = 1,
    ):
        patches = []

        for (axes_id, channels) in images.items():
            for i in ("r", "g", "b"):
                channels[i] = self._scale_array(channels[i], 0, 1)

            rgb_map = np.stack((channels["r"], channels["g"], channels["b"]), 2)
            rgb_map = self._set_background_color(rgb_map, background_color)

            self.get_axes(axes_id).imshow(
                rgb_map,
                extent=params[axes_id].extent,
                interpolation="nearest",
                aspect="auto",
            )

            patches.append(
                mpatches.Patch(color=params[axes_id].channel, label=params[axes_id].label)
            )

    def _save_pickle(self, filename: str):
        import pickle

        with open(filename, "wb") as f:
            pickle.dump(self.figure, f)

    def save(
        self,
        pic_filename: Optional[str] = None,
        pickle_filename: Optional[str] = None,
        dpi: int = 120,
        pdf_object: Optional[PdfMerger] = None,
        pdf_tmp_path: Optional[str] = None,
    ):
        images: Dict[str, Dict[str, np.ndarray]] = {}
        imparams = {}
        patches_map: dict[str, list[mpatches.Patch]] = {}

        for (data, params) in self.pictures:
            if not params.is_density_plot:
                self._scatter_points(data, params)
            else:
                hist = self._get_hist(
                    data[params.x],
                    data[params.y],
                    params.resolution,
                    params.extent,
                    None if params.weights is None else data[params.weights],
                )

                if params.id not in images:
                    images[params.id] = {
                        "r": np.zeros(hist.shape),
                        "g": np.zeros(hist.shape),
                        "b": np.zeros(hist.shape),
                    }

                images[params.id][params.channel] += hist
                imparams[params.id] = params

                if params.label is not None:
                    if params.id not in patches_map:
                        patches_map[params.id] = []

                    patches_map[params.id].append(
                        mpatches.Patch(color=params.channel, label=params.label)
                    )

        self._draw_images(images, imparams, 0.85)

        for axes_id, patches in patches_map.items():
            self.get_axes(axes_id).legend(handles=patches, loc="upper left")

        if pic_filename is not None:
            self.figure.savefig(pic_filename, bbox_inches="tight")

        if pickle_filename is not None:
            self._save_pickle(pickle_filename)

        if pdf_object is not None and pdf_tmp_path is not None:
            self.figure.savefig(pdf_tmp_path, bbox_inches="tight")
            pdf_object.append(pdf_tmp_path)

        def clear(axes: Axes):
            while len(axes.artists) != 0:
                axes.artists[0].remove()

            while len(axes.lines) != 0:
                axes.lines[0].remove()

            while len(axes.images) != 0:
                axes.images[0].remove()

        self.pictures.clear()
        self._do_for_all_axes(clear)
