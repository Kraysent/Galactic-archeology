import numpy as np
import pandas
from amuse.ic.plummer import new_plummer_sphere
from amuse.lab import Particles, ScalarQuantity, nbody_system, units

from omtool.core.datamodel import Snapshot


class SnapshotCreator:
    @staticmethod
    def construct_plummer_sphere(
        number_of_particles: int, mass: ScalarQuantity, radius: ScalarQuantity
    ) -> Snapshot:
        convert_nbody = nbody_system.nbody_to_si(mass, radius)
        particles = new_plummer_sphere(number_of_particles, convert_nbody)
        particles.is_barion = [True] * len(particles)

        return Snapshot(particles, 0 | units.Myr)

    @staticmethod
    def construct_from_csv(path: str, delimiter: str) -> Snapshot:
        """
        Read the list of particles from the CSV file on form
        x,y,z,vx,vy,vz,m,is_barion
        """
        table = pandas.read_csv(path, delimiter=delimiter, index_col=False)
        table["barion"].map({"True": True, "False": False})
        particles = Particles(len(table.iloc[:, 0]))
        particles.x = np.array(table["x"]) | units.kpc
        particles.y = np.array(table["y"]) | units.kpc
        particles.z = np.array(table["z"]) | units.kpc
        particles.vx = np.array(table["vx"]) | units.kms
        particles.vy = np.array(table["vy"]) | units.kms
        particles.vz = np.array(table["vz"]) | units.kms
        particles.mass = np.array(table["m"]) | 232500 * units.MSun
        particles.is_barion = table["barion"]

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot

    @staticmethod
    def construct_single_particle(mass: ScalarQuantity) -> Snapshot:
        """
        Create snapshot from the single mass value at the origin.
        """
        particles = Particles(1)
        particles[0].position = [0, 0, 0] | units.kpc
        particles[0].velocity = [0, 0, 0] | units.kms
        particles[0].mass = mass
        particles[0].is_barion = True

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot
