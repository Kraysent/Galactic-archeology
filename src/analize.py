from amuse.units.quantities import ScalarQuantity
from io.nemo_to_snapshot_reader import NEMOToSnapshotReader
from snapshot import Snapshot
from io.tsv_to_snapshot_reader import TsvToSnapshotReader
from io.snapshot_to_nemo_writer import SnapshotToNEMOWriter
from falcon_integrator import FalconIntegrator
import matplotlib.pyplot as plt
import numpy as np
from amuse.lab import units
from amuse.datamodel.particles import Particles

reader = TsvToSnapshotReader()
host_snapshot = reader.convert('input/host.txt')
sat_snapshot = reader.convert('input/sat.txt')
sat_snapshot.particles.x += 100 | units.kpc
sat_snapshot.particles.vy += 130 | units.kms
sum_particles = Particles()
sum_particles.add_particles(host_snapshot.particles)
sum_particles.add_particles(sat_snapshot.particles)

print(sum_particles.total_mass().value_in(units.MSun))

sum_snapshot = Snapshot(sum_particles, host_snapshot.timestamp)

print('TSV read')

writer = SnapshotToNEMOWriter()
writer.write(sum_snapshot, 'output/sum.nemo')

print('NEMO wrote')

# integrator = FalconIntegrator()
# integrator.set_params(eps = 0.1, kmax = 4, tstop = 1, step = 0.125)
# integrator.integrate('input/sum.nemo', 'output/result.nemo')

# print('gyrfalcON integrated')

# reader = NEMOToSnapshotReader('output/result.nemo')
# fig, (ax1, ax2) = plt.subplots(ncols=2)

# while reader.next_frame():
#     snapshot = reader.convert()
#     print(snapshot.timestamp)

#     ax1.set_ylim(-1000, 1000)
#     ax1.set_xlim(-500, 500)
#     ax2.set_ylim(-1000, 1000)
#     ax2.set_xlim(-500, 500)
#     ax1.set_xlabel('x')
#     ax1.set_ylabel('y')
#     ax2.set_xlabel('z')
#     ax2.set_ylabel('y')

#     ax1.plot(snapshot.particles.x.value_in(units.kpc), snapshot.particles.y.value_in(units.kpc), 'r,')
#     ax2.plot(snapshot.particles.z.value_in(units.kpc), snapshot.particles.y.value_in(units.kpc), 'r,')
#     plt.suptitle('Time: {} Myr'.format(snapshot.timestamp.value_in(units.Myr)))
#     plt.savefig('output/{}.png'.format(np.round(snapshot.timestamp.value_in(units.Myr), 2)))
#     ax1.clear()
#     ax2.clear()
