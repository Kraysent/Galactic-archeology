from collections import namedtuple
import pyfalcon
from amuse.lab import VectorQuantity, ScalarQuantity, units
from omtool.datamodel import Snapshot

Units = namedtuple("Units", "L V M T")
u = Units(
    L = units.kpc,
    M = 232500 * units.MSun,
    T = units.Gyr,
    V = units.kms
)

def get_potentials(snapshot: Snapshot, eps: ScalarQuantity) -> VectorQuantity:
    pos = snapshot.particles.position.value_in(u.L)
    mass = snapshot.particles.mass.value_in(u.M)
    eps = eps.value_in(u.L)

    _, pot = pyfalcon.gravity(pos, mass, eps)

    return pot | u.L ** 2 / u.T ** 2

