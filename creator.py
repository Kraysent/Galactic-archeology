from amuse.datamodel.particles import Particle, Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from archeology.creation import SnapshotBuilder
from archeology.datamodel.snapshot import Snapshot


def create(datadir: str):
    host = Snapshot.from_csv(f'{datadir}/models/host.txt', ' ')
    sat = Snapshot.from_csv(f'{datadir}/models/sat.txt', ' ')

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

    print('Building model...')
    sat_offset = get_offset(10 | units.kpc)
    sat_velocity = get_velocity(66 | units.kms, 1, 0 | units.kms)
    builder = SnapshotBuilder()

    black_holes = Particles(2)
    black_holes[0].position = [0., 0., 0.] | units.kpc
    black_holes[0].velocity = [0., 0., 0.] | units.kms
    black_holes[0].mass = 4e8 | units.MSun

    black_holes[1].position = sat_offset
    black_holes[1].velocity = sat_velocity
    black_holes[1].mass = 1e8 | units.MSun

    builder.add_particles(black_holes[:1])
    builder.add_snapshot(host)
    builder.add_particles(black_holes[1:])
    # builder.add_snapshot(sat, sat_offset, sat_velocity)

    builder.to_fits(f'{datadir}/models/bh_100x_flat_without_galaxy.fits')
    print('Model built.')
