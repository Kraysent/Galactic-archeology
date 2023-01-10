"""
Struct that holds together particle set and timestamp that it describes.
"""

import contextlib
import pandas as pd
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity
from astropy.io import fits

fields = {
    "x": 1 | units.kpc,
    "y": 1 | units.kpc,
    "z": 1 | units.kpc,
    "vx": 1 | units.kms,
    "vy": 1 | units.kms,
    "vz": 1 | units.kms,
    "mass": 1 | units.MSun,
}

optional_fields = {
    "is_barion": None,
}


class Snapshot:
    """
    Struct that holds together particle set and timestamp that it describes.
    """

    def __init__(
        self,
        particles: Particles = Particles(),
        timestamp: ScalarQuantity = 0 | units.Myr,
    ):
        self._particles_df = pd.DataFrame(columns=fields.keys())

        for field, unit in fields.items():
            if unit is None:
                self._particles_df[field] = getattr(particles, field)
            else:
                self._particles_df[field] = getattr(particles, field) / unit

        for field, unit in optional_fields.items():
            with contextlib.suppress(AttributeError):
                if unit is None:
                    self._particles_df[field] = getattr(particles, field)
                else:
                    self._particles_df[field] = getattr(particles, field) / unit

        self._particles = particles
        self.timestamp = timestamp

    def get_amuse_particles(self) -> Particles:
        particles = Particles(len(self._particles_df))

        for column in self._particles_df.columns:
            unit = fields[column]
            if unit is None:
                setattr(particles, column, self._particles_df[column])
            else:
                setattr(particles, column, self._particles_df[column] * unit)

        return particles

    @property
    def particles(self) -> Particles:
        """
        Returns AMUSE Particles object.
        """
        return self._particles

    @particles.setter
    def particles(self, particles: Particles):
        """
        Deprecated. Sets particles from AMUSE Particles object. Exists only for backwards compatibility.
        """
        self._particles = particles

    def __getitem__(self, value) -> "Snapshot":
        return Snapshot(self.particles[value], self.timestamp)

    def __add__(self, other: "Snapshot") -> "Snapshot":
        if self.timestamp != other.timestamp:
            raise RuntimeError("Tried to sum snapshots with different timestamps.")

        particles = Particles()
        particles.add_particles(self.particles)
        particles.add_particles(other.particles)

        return Snapshot(particles, self.timestamp)

    def add(self, other: "Snapshot", ignore_timestamp: bool = False):
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

        for (key, val) in fields.items() + optional_fields.items():
            if not hasattr(self.particles, key):
                continue

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

    def to_csv(self, filename: str):
        df = pd.DataFrame(columns=fields.keys())

        for key, val in fields.items() + optional_fields.items():
            if not hasattr(self.particles, key):
                continue

            array = getattr(self.particles, key)

            if val is None:
                val = 1

            df[key] = array / val

        df.to_csv(filename)
