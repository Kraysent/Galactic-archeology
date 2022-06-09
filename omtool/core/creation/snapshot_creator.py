from omtool.core.datamodel import Snapshot
from amuse.ic.plummer import new_plummer_sphere
from amuse.lab import units, ScalarQuantity, nbody_system

class SnapshotCreator:
    @staticmethod
    def construct_plummer_sphere(number_of_particles: int, mass: ScalarQuantity, radius: ScalarQuantity):
        convert_nbody = nbody_system.nbody_to_si(mass, radius)
        particles = new_plummer_sphere(number_of_particles, convert_nbody)
        particles.is_barion = [True] * len(particles)

        return Snapshot(particles, 0 | units.Myr)
