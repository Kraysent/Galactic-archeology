import unsio
from snapshot import Snapshot
from amuse.datamodel.particles import Particles
from amuse.lab import units

class NEMOToSnapshotReader:
    def __init__(self, filename: str) -> None:
        self.snapfile = unsio.CunsIn(filename, 'all', 'all')

    def convert(self) -> Snapshot:
        pos  = self.snapfile.getArrayF('all', 'pos')[1].reshape(-1,3).copy().transpose()
        vel  = self.snapfile.getArrayF('all', 'vel')[1].reshape(-1,3).copy().transpose()
        mass = self.snapfile.getArrayF('all', 'mass')[1].copy()
        time = self.snapfile.getValueF('time')[1]

        result = Particles(size = len(pos[0]))
        result.x = pos[0] | units.kpc
        result.y = pos[1] | units.kpc
        result.z = pos[2] | units.kpc

        result.vx = vel[0] | units.kms
        result.vy = vel[1] | units.kms
        result.vz = vel[2] | units.kms

        result.mass = mass * 232500 | units.MSun

        return Snapshot(result, time | units.Gyr)

    def next_frame(self) -> bool:
        return bool(self.snapfile.nextFrame(''))