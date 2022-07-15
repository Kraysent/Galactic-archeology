from dataclasses import dataclass
from typing import List, Optional, Tuple

from marshmallow import Schema, fields, post_load


@dataclass
class PlotParameters:
    grid: bool = False
    xlim: Tuple[Optional[int], Optional[int]] = (None, None)
    ylim: Tuple[Optional[int], Optional[int]] = (None, None)
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
    coords: Tuple[int, ...]
    params: PlotParameters


@dataclass
class Config:
    output_dir: str
    title: str
    figsize: Tuple[int, ...]
    pic_filename: str
    panels: List[PanelConfig]


class PlotParametersSchema(Schema):
    grid = fields.Bool()
    xlim = fields.Tuple((fields.Int(), fields.Int()))
    ylim = fields.Tuple((fields.Int(), fields.Int()))
    xlabel = fields.Str()
    ylabel = fields.Str()
    xticks = fields.List(fields.Int())
    yticks = fields.List(fields.Int())
    title = fields.Str()
    ticks_direction = fields.Str()
    xscale = fields.Str()
    basex = fields.Int()
    yscale = fields.Str()
    basey = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        return PlotParameters(**data)


class PanelSchema(Schema):
    id = fields.Str(required=True)
    coords = fields.Tuple(
        (fields.Float(), fields.Float(), fields.Float(), fields.Float()), load_default=(0, 1, 1, 1)
    )
    params = fields.Nested(PlotParametersSchema)

    @post_load
    def make(self, data, **kwargs):
        return PanelConfig(**data)


class VisualizerConfigSchema(Schema):
    output_dir = fields.Str(required=True)
    title = fields.Str(load_default="")
    figsize = fields.Tuple((fields.Int(), fields.Int()), load_default=(16, 9))
    pic_filename = fields.Str(load_default="img-{i:03d}.png")
    panels = fields.List(fields.Nested(PanelSchema), required=True)

    @post_load
    def make(self, data, **kwargs):
        return Config(**data)
