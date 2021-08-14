from amuse.datamodel.particles import Particles
from amuse.lab import units, ScalarQuantity
from utils.snapshot import Snapshot
import numpy as np

class TsvToSnapshotReader:
    def __init__(self) -> None:
        pass

    def convert(self, filename: str, timestamp: ScalarQuantity = 0 | units.Myr) -> Snapshot:
        data = self._read_numerical_csv(filename, ['x', 'y', 'z', 'vx', 'vy', 'vz', 'm'])
        particles = Particles(size = len(data['x']))
        particles.x = data['x'] | units.kpc
        particles.y = data['y'] | units.kpc
        particles.z = data['z'] | units.kpc
        particles.vx = data['vx'] | units.kms
        particles.vy = data['vy'] | units.kms
        particles.vz = data['vz'] | units.kms
        particles.mass = data['m'] * 232500 | units.MSun
        
        return Snapshot(particles, 0 | units.Myr)

    def _read_numerical_csv(self, filename: str, fields: list):
        f = open(filename)
        output = {}

        for field in fields:
            output[field] = []
        
        for line in f:
            curr = line.split(' ')

            if len(curr) < len(fields):
                raise Exception('Not enough fields in file')

            for i in range(len(fields)):
                output[fields[i]].append(float(curr[i]))

        for field in fields:
            output[field] = np.array(output[field])

        return output
