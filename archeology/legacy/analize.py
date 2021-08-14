from amuse.units.quantities import ScalarQuantity
from nemo_to_snapshot_reader import NEMOToSnapshotReader
from utils.snapshot import Snapshot
from tsv_to_snapshot_reader import TsvToSnapshotReader
from snapshot_to_nemo_writer import SnapshotToNEMOWriter
import matplotlib.pyplot as plt
import numpy as np
from amuse.lab import units
from amuse.datamodel.particles import Particles

def get_snapshot() -> Snapshot: 
    reader = TsvToSnapshotReader()
    host_snapshot = reader.convert('input/host.txt')
    sat_snapshot = reader.convert('input/sat.txt')
    sat_snapshot.particles.x += 125 | units.kpc
    sat_snapshot.particles.vx -= 75 | units.kms
    sat_snapshot.particles.vy += 75 | units.kms
    sat_snapshot.particles.vz += 75 | units.kms
    sum_particles = Particles()
    sum_particles.add_particles(host_snapshot.particles)
    sum_particles.add_particles(sat_snapshot.particles)
    sum_snapshot = Snapshot(sum_particles, host_snapshot.timestamp)
    return sum_snapshot

def write_snapshot(snapshot: Snapshot):
    writer = SnapshotToNEMOWriter()
    writer.write(snapshot, 'output/new.nemo')

def read(filename: str):
    reader = NEMOToSnapshotReader(filename)
    _, (ax1, ax2) = plt.subplots(ncols=2)

    while reader.next_frame():
        snapshot = reader.convert()
        print(snapshot.timestamp)

        ax1.set_ylim(-1000, 1000)
        ax1.set_xlim(-500, 500)
        ax2.set_ylim(-1000, 1000)
        ax2.set_xlim(-500, 500)
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax2.set_xlabel('z')
        ax2.set_ylabel('y')

        ax1.plot(snapshot.particles.x.value_in(units.kpc), snapshot.particles.y.value_in(units.kpc), 'ro', markersize = 0.05)
        ax2.plot(snapshot.particles.z.value_in(units.kpc), snapshot.particles.y.value_in(units.kpc), 'ro', markersize = 0.05)
        plt.suptitle('Time: {} Myr'.format(snapshot.timestamp.value_in(units.Myr)))
        plt.savefig('output/{}.png'.format(np.round(snapshot.timestamp.value_in(units.Myr), 2)))
        ax1.clear()
        ax2.clear()

snapshot = get_snapshot()
print('TSV read')

write_snapshot(snapshot)
print('NEMO wrote')

# read('output/sum_out.nemo')
# print('NEMO read')