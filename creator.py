from pathlib import Path

from omtool.creation import CreationConfig, Object, SnapshotBuilder, Type
from omtool.datamodel import Snapshot, profiler


def create(config: CreationConfig):
    builder = SnapshotBuilder()

    if not config.overwrite:
        if Path(config.output_file).is_file():
            raise Exception(f'Output file ({config.output_file}) exists and "overwrite" option in creation config file is false (default)')

    @profiler('Creation')
    def loop_creation_stage(object: Object):
        if object.type == Type.CSV:
            curr_snapshot = Snapshot.from_csv(object.path, object.delimeter)
        elif object.type == Type.BODY:
            curr_snapshot = Snapshot.from_mass(object.mass)
        
        curr_snapshot.particles.position += object.position
        curr_snapshot.particles.velocity += object.velocity

        builder.add_snapshot(curr_snapshot)

    for object in config.objects:
        loop_creation_stage(object)

    builder.to_fits(config.output_file)
