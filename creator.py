from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from archeology.creation import SnapshotBuilder
from archeology.iotools import CSVReadManager, FITSWriteManager

host_manager = CSVReadManager('data/models/host.txt', ' ')
sat_manager = CSVReadManager('data/models/sat.txt', ' ')

host = host_manager.read_data()
sat = sat_manager.read_data()

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

builder = SnapshotBuilder()
builder.add_particles(host.particles)
builder.add_particles(sat.particles, 
    get_offset(150 | units.kpc), 
    get_velocity(113 | units.kms, 0.5)
)

manager = FITSWriteManager('data/models/flat_example.fits')
manager.write_data(builder.get_result())
