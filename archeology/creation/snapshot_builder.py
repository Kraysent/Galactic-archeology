from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import VectorQuantity
from archeology.datamodel import Snapshot
from archeology.iotools import FITSWriteManager

class SnapshotBuilder:
    def __init__(self):
        self.snapshot = Snapshot(Particles(), 0 | units.Myr)

    def add_snapshot(self,
        snapshot: Snapshot, 
        offset: VectorQuantity = [0, 0, 0] | units.kpc, 
        velocity: VectorQuantity = [0, 0, 0] | units.kms
    ):
        snapshot.particles.position += offset
        snapshot.particles.velocity += velocity
    
        self.snapshot = self.snapshot + snapshot

    def add_particles(self, particles: Particles):
        self.snapshot.particles.add_particles(particles)

    def get_result(self) -> Snapshot:
        self.snapshot.particles.move_to_center()

        return self.snapshot

    def to_fits(self, filename: str):
        self.snapshot.particles.move_to_center()

        manager = FITSWriteManager(filename)
        manager.write_data(self.snapshot)
