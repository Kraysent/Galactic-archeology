import logging
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from archeology.creation import SnapshotBuilder
from archeology.datamodel import Snapshot, Config


def create(config: Config):
    builder = SnapshotBuilder()

    for object in config.objects:
        if object['type'] == 'csv':
            curr_snapshot = Snapshot.from_csv(object['path'], object['delimeter'])
        elif object['type'] == 'body':
            curr_snapshot = Snapshot.from_mass(object['mass'] | units.MSun)
        
        curr_snapshot.particles.position += object['position'] | units.kpc
        curr_snapshot.particles.velocity += object['velocity'] | units.kms

        builder.add_snapshot(curr_snapshot)

    builder.to_fits(config.output_file)


def create1(host_fn: str, sat_fn: str, output_fn: str):
    '''
    output_fn: str - filename which saved snapshot would have

    host_fn: str - filename of host snapshot *.csv file

    sat_fn: str - filename of satellite snapshot *.csv file
    '''
    host = Snapshot.from_csv(host_fn, ' ')
    sat = Snapshot.from_csv(sat_fn, ' ')

    def get_offset(distance: ScalarQuantity):
        offset = [0, 0, 0] | units.kpc
        offset[0] = distance

        return offset

    def get_velocity(module: ScalarQuantity, pointing: float, zvalue: ScalarQuantity):
        v_r = module / (pointing ** 2 + 1) ** 0.5
        v_tau = pointing * v_r

        vel = [0, 0, 0] | units.kms
        vel[0] = - v_r
        vel[1] = v_tau
        vel[2] = zvalue

        return vel

    logging.info('Building model...')
    sat_offset = get_offset(10 | units.kpc)
    sat_velocity = get_velocity(66 | units.kms, 1, 0 | units.kms)
    builder = SnapshotBuilder()

    black_holes = Particles(2)
    black_holes[0].position = [0., 0., 0.] | units.kpc
    black_holes[0].velocity = [0., 0., 0.] | units.kms
    black_holes[0].mass = 4e8 | units.MSun

    black_holes[1].position = [10, 0, 0] | units.kpc
    black_holes[1].velocity = [-66, 0, 0] | units.kms
    black_holes[1].mass = 1e8 | units.MSun

    builder.add_particles(black_holes[:1])
    builder.add_snapshot(host)
    builder.add_particles(black_holes[1:])
    # builder.add_snapshot(sat, sat_offset, sat_velocity)

    builder.to_fits(output_fn)
    logging.info(f'Model has been written to {output_fn}.')
