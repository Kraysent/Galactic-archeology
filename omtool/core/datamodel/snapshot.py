"""
Struct that holds together particle set and timestamp that it describes.
"""
import numpy as np
import pandas
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity
from astropy.io import fits


class Snapshot:
    """
    Struct that holds together particle set and timestamp that it describes.
    """

    fields = {
        "x": units.kpc,
        "y": units.kpc,
        "z": units.kpc,
        "vx": units.kms,
        "vy": units.kms,
        "vz": units.kms,
        "mass": units.MSun,
        "is_barion": None,
    }

    def __init__(
        self,
        particles: Particles = Particles(),
        timestamp: ScalarQuantity = 0 | units.Myr,
    ):
        self.particles = particles
        self.timestamp = timestamp

    def __getitem__(self, value) -> "Snapshot":
        return Snapshot(self.particles[value], self.timestamp)

    def __add__(self, other: "Snapshot") -> "Snapshot":
        if self.timestamp != other.timestamp:
            raise RuntimeError("Tried to sum snapshots with different timestamps.")

        particles = Particles()
        particles.add_particles(self.particles)
        particles.add_particles(other.particles)

        return Snapshot(particles, self.timestamp)

    def add(self, other: "Snapshot", ignore_timestamp=False):
        """
        Adds other snapshot to this one. If ignore_timestamps is False,
        does not change timestamp. Otherwise RuntimeError would be thrown if
        timestamps are different.
        """
        if not ignore_timestamp and (self.timestamp != other.timestamp):
            raise RuntimeError("Tried to sum snapshots with different timestamps.")

        self.particles.add_particles(other.particles)

    def to_fits(self, filename: str, append: bool = False):
        """
        Writes the snapshot into FITS file.
        """
        cols = []

        for (key, val) in Snapshot.fields.items():
            array = getattr(self.particles, key)
            fmt = "L"

            if val is not None:
                array = array.value_in(val)
                fmt = "E"

            col = fits.Column(name=key, unit=str(val), format=fmt, array=array)
            cols.append(col)

        cols = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(cols)
        hdu.header["TIME"] = self.timestamp.value_in(units.Myr)

        if append:
            try:
                fits.append(filename, hdu.data, hdu.header)
            except Exception:
                hdu.writeto(filename, overwrite=True)
        else:
            hdu.writeto(filename, overwrite=True)

    @staticmethod
    def from_csv(filename: str, delimiter: str = ",") -> "Snapshot":
        """
        Read the list of particles from the CSV file on form
        x,y,z,vx,vy,vz,m,is_barion
        """
        table = pandas.read_csv(filename, delimiter=delimiter, index_col=False)
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
    def from_mass(mass: ScalarQuantity) -> "Snapshot":
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
