from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import VectorQuantity
from archeology.datamodel import Snapshot
import logging
import numpy as np

class SnapshotBuilder:
    def __init__(self):
        self.snapshot = Snapshot(Particles(), 0 | units.Myr)

    def add_snapshot(self,
        snapshot: Snapshot, 
        offset: VectorQuantity = [0, 0, 0] | units.kpc, 
        velocity: VectorQuantity = [0, 0, 0] | units.kms
    ):
        logging.info(f'Adding snapshot of {len(snapshot.particles)} particles.')

        snapshot.particles.position += offset
        snapshot.particles.velocity += velocity

        min_mass = snapshot.particles.mass.value_in(units.MSun).min()
        max_mass = snapshot.particles.mass.value_in(units.MSun).max()
        meanpos = np.mean(snapshot.particles.position, axis = 1).value_in(units.kpc)
        stdpos = np.std(snapshot.particles.position, axis = 1).value_in(units.kpc)
        meanvel = np.mean(snapshot.particles.velocity, axis = 1).value_in(units.kms)
        stdvel = np.std(snapshot.particles.velocity, axis = 1).value_in(units.kms)

        logging.info(f'm span: {min_mass:.0f} - {max_mass:.0f} MSun')
        logging.info(f'r span: ({meanpos[0]:.0f}, {meanpos[1]:.0f}, {meanpos[2]:.0f}) +- ({stdpos[0]:.0f}, {stdpos[1]:.0f}, {stdpos[2]:.0f}) kpc')
        logging.info(f'v span: ({meanvel[0]:.0f}, {meanvel[1]:.0f}, {meanvel[2]:.0f}) +- ({stdvel[0]:.0f}, {stdvel[1]:.0f}, {stdvel[2]:.0f}) kpc')

        self.snapshot = self.snapshot + snapshot
        logging.info('Snapshot added.')

    def add_particles(self, particles: Particles):
        self.snapshot.particles.add_particles(particles)

    def get_result(self) -> Snapshot:
        self.snapshot.particles.move_to_center()

        return self.snapshot

    def to_fits(self, filename: str):
        self.snapshot.particles.move_to_center()
        self.snapshot.to_fits(filename)
