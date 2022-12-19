from marshmallow import Schema, fields, post_load

from omtool.visualizer import PanelConfig, PlotParameters, VisualizerConfig


class PlotParametersSchema(Schema):
    grid = fields.Bool()
    xlim = fields.List(fields.Float())
    ylim = fields.List(fields.Float())
    xlabel = fields.Str()
    ylabel = fields.Str()
    xticks = fields.List(fields.Float())
    yticks = fields.List(fields.Float())
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
    id = fields.Str(required=True, description="Id of the panel. Should be unique.")
    coords = fields.List(
        fields.Float(),
        load_default=(0, 1, 1, 1),
        description="Position and size of the graph in form of [left, bottom, width, height]. "
        "Coordinates are counted from the left bottom of the picture.",
    )
    params = fields.Nested(
        PlotParametersSchema,
        description="Parameters of the graph box. They should be given the same names as ones in "
        "matplotlib.pyplot (and proper values) as most of them are just passed along to it.",
    )

    @post_load
    def make(self, data, **kwargs):
        return PanelConfig(**data)


class VisualizerConfigSchema(Schema):
    output_dir = fields.Str(
        required=True, description="Output directory where the images would be saved."
    )
    title = fields.Str(
        load_default="",
        description="Title template. Use {time} to get time in Myr. One can use standart python "
        "formatters to format number of digits, rounding, etc.",
    )
    figsize = fields.List(fields.Int(), load_default=(16, 9), description="Figure size in inches.")
    pic_filename = fields.Str(
        load_default=None,
        description="Pictures will be saved in output_dir with this filename. "
        "{i} is iteration number.",
    )
    pickle_filename = fields.Str(
        load_default=None,
        description="Pickle files will be saved in output_dir with this filename. "
        "{i} is iteration number.",
    )
    panels = fields.List(
        fields.Nested(PanelSchema),
        required=True,
        description="List of panels, their layouts and properties.",
    )
    pdf_name = fields.Str(
        load_default=None,
        description="Name of the pdf file to save all snapshot pictures to.",
    )

    @post_load
    def make(self, data, **kwargs):
        return VisualizerConfig(**data)
