import numpy as np
import pyfalcon
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from archeology.datamodel import Snapshot
from archeology.iotools import FITSReadManager, FITSWriteManager, NEMOIOManager


class PyfalconIntegrator:
    def __init__(self, 
        snapshot: Snapshot, 
        time: ScalarQuantity, 
        eps: ScalarQuantity
    ):
        self.pos, self.vel, self.mass = self._get_params(snapshot)
        self.eps = eps.value_in(units.kpc)
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.time = time.value_in(units.Myr)

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(units.kpc)
        vel = snapshot.particles.velocity.value_in(units.kms)
        mass = snapshot.particles.mass.value_in(units.MSun)

        pos = np.squeeze(pos.reshape((1, pos.shape[1] * 3)))
        vel = np.squeeze(pos.reshape((1, vel.shape[1] * 3)))
        return (pos, vel, mass)

    def leapfrog(self, dt):
        self.vel += self.acc * (dt / 2)
        self.pos += self.vel * dt
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.vel += self.acc * (dt / 2)
        self.time += dt

    def get_snapshot(self):
        N = len(self.mass)
        snapshot = Snapshot(Particles(N), self.time | units.Myr)
        

manager = NEMOIOManager('output/models/flat_model_out.nemo')
fits_manager = FITSWriteManager('test.fits')

while manager.next_frame():
    snapshot = manager.get_data()
    # fits_manager.append_data(snapshot)
    print(f'Read {snapshot.timestamp.value_in(units.Myr)}')

# i = 0

# fits_manager = FITSReadManager('test.fits')

# while fits_manager.next_frame():
#     snapshot = fits_manager.read_data()
#     print(snapshot.timestamp.value_in(units.Myr))
#     print(snapshot.particles.center_of_mass().length().value_in(units.kpc))
    
#     i += 1
