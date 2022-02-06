from amuse.lab import units

from omtool.creation import SnapshotBuilder
from omtool.creation import CreationConfig, Type
from omtool.datamodel import Snapshot


def create(config: CreationConfig):
    builder = SnapshotBuilder()

    for object in config.objects:
        if object.type == Type.CSV:
            curr_snapshot = Snapshot.from_csv(object.path, object.delimeter)
        elif object.type == Type.BODY:
            curr_snapshot = Snapshot.from_mass(object.mass)
        
        curr_snapshot.particles.position += object.position
        curr_snapshot.particles.velocity += object.velocity

        builder.add_snapshot(curr_snapshot)

    builder.to_fits(config.output_file)
