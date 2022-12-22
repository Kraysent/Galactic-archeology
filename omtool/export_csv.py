from omtool.core import datamodel


def export_csv(input_file: str, output_file: str, snapshot_index: int):
    generator = datamodel.from_fits(input_file, snapshot_index=snapshot_index, limit=1)
    next(generator).to_csv(output_file)
