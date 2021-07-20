import numpy as np
from utils.snapshot import Snapshot
from amuse.lab import units
import unsio

class SnapshotToNEMOWriter:
    def __init__(self) -> None:
        pass

    def _get_flat_array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        res = np.stack((x, y, z))
        res = res.transpose()
        res = res.reshape((len(x) * 3))
        return res.astype(np.float32)

    def write(self, snapshot: Snapshot, filename: str):
        x = snapshot.particles.x.value_in(units.kpc)
        y = snapshot.particles.y.value_in(units.kpc)
        z = snapshot.particles.z.value_in(units.kpc)
        vx = snapshot.particles.vx.value_in(units.kms)
        vy = snapshot.particles.vy.value_in(units.kms)
        vz = snapshot.particles.vz.value_in(units.kms)
        mass = snapshot.particles.mass.value_in(units.MSun) / 232500

        time = snapshot.timestamp.value_in(units.Gyr)
        pos = self._get_flat_array(x, y, z)
        vel = self._get_flat_array(vx, vy, vz)

        mass = mass.astype(np.float32)

        out = unsio.CunsOut(filename, 'nemo')
        status = out.setValueF('time', time)
        status = out.setArrayF('all', 'pos', pos)
        status = out.setArrayF('all', 'vel', vel)
        status = out.setArrayF('all', 'mass', mass)

        out.save()
        out.close()


