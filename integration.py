import numpy as np
import pyfalcon
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from archeology.datamodel import Snapshot
from archeology.iotools import FITSReadManager, FITSWriteManager, NEMOIOManager
import time

class PyfalconIntegrator:
    def __init__(self, 
        snapshot: Snapshot,
        eps: ScalarQuantity,
        kmax: float
    ):
        self.pos, self.vel, self.mass, self.time = self._get_params(snapshot)
        self.eps = eps.value_in(units.kpc)
        self.dt = 0.5 ** kmax
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(units.kpc)
        vel = snapshot.particles.velocity.value_in(units.kms)
        mass = snapshot.particles.mass.value_in(232500 * units.MSun)
        time = snapshot.timestamp.value_in(units.Gyr)
        
        return (pos, vel, mass, time)

    def leapfrog(self):
        self.vel += self.acc * (self.dt / 2)
        self.pos += self.vel * self.dt
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.vel += self.acc * (self.dt / 2)
        self.time += self.dt

    def get_snapshot(self) -> Snapshot:
        N = len(self.mass)
        snapshot = Snapshot(Particles(N), self.time | units.Myr)
        pos = self.pos.reshape(N, -1, order = 'F') | units.kpc
        vel = self.vel.reshape(N, -1, order = 'F') | units.kms
        mass = self.mass | 232500 * units.MSun
        snapshot.particles.position = pos
        snapshot.particles.velocity = vel
        snapshot.particles.mass = mass
        snapshot.timestamp = self.time | units.Gyr

        return snapshot

manager = FITSReadManager('output/models/flat_model_in.fits')
out_manager = FITSWriteManager('output/models/flat_model_out.fits')

manager.next_frame()
snapshot = manager.read_data()
integrator = PyfalconIntegrator(snapshot, 0.2 | units.kpc, 6)

for i in range(100):
    start = time.time()
    integrator.leapfrog()

    if i % 8 == 0:
        snapshot = integrator.get_snapshot()
        out_manager.append_data(snapshot)

    print(f'{np.round(time.time() - start, 2)}\t{np.round(integrator.time, 4)}')
