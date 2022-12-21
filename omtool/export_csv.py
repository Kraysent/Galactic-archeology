from omtool.core.datamodel import Snapshot
from omtool.io_service import readers


def export_csv(input_file: str, output_file: str, snapshot_index: int):
    generator = readers.from_fits(input_file, snapshot_index=snapshot_index, limit=1)
    particles, timestamp = next(generator)
    snapshot = Snapshot(particles, timestamp)
    snapshot.to_csv(output_file)
