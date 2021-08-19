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

    def get_velocity(module: ScalarQuantity, pointing: float):
        v_r = module / (pointing ** 2 + 1) ** 0.5
        v_tau = pointing * v_r

        vel = [0, 0, 0] | units.kms
        vel[0] = - v_r
        vel[1] = v_tau

        return vel

    print('Building model...')
    builder = SnapshotBuilder()
    builder.add_snapshot(host)
    builder.add_snapshot(sat, 
        get_offset(150 | units.kpc), 
        get_velocity(113 | units.kms, 0.75)
    )

    builder.to_fits(f'{datadir}/models/example.fits')
    print('Model built.')
