from archeology.datamodel import Snapshot, snapshot
from amuse.datamodel import Particles
from amuse.lab import units
import numpy as np
import pandas

class CSVReadManager:
    def __init__(self, filename: str, delimiter: str = ','):
        self.filename = filename
        self.delimiter = delimiter

    def read_data(self) -> Snapshot:
        table = pandas.read_csv(self.filename, delimiter = self.delimiter)
        particles = Particles(len(table.iloc[:, 0]))
        particles.x = np.array(table['x']) | units.kpc
        particles.y = np.array(table['y']) | units.kpc
        particles.z = np.array(table['z']) | units.kpc
        particles.vx = np.array(table['vx']) | units.kms
        particles.vy = np.array(table['vy']) | units.kms
        particles.vz = np.array(table['vz']) | units.kms
        particles.mass = np.array(table['m']) | units.MSun

        snapshot = Snapshot(particles, 0| units.Myr)

        return snapshot