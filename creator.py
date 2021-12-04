from amuse.lab import units

from omtool.creation import SnapshotBuilder
from omtool.datamodel import Snapshot, Config


def create(config: Config):
    builder = SnapshotBuilder()

    for object in config['objects']:
        if object['type'] == 'csv':
            curr_snapshot = Snapshot.from_csv(object['path'], object['delimeter'])
        elif object['type'] == 'body':
            curr_snapshot = Snapshot.from_mass(object['mass'])
        
        curr_snapshot.particles.position += object['position']
        curr_snapshot.particles.velocity += object['velocity']

        builder.add_snapshot(curr_snapshot)

    builder.to_fits(config['output_file'])
