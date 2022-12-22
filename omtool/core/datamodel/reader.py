import gc
from typing import Iterator

import numpy as np
import pandas as pd
from amuse.datamodel.particles import Particle, Particles
from amuse.lab import units
from astropy.io import fits
from astropy.io.fits.hdu.table import BinTableHDU

from omtool.core.datamodel.snapshot import Snapshot, fields


def from_fits(
    filename: str,
    snapshot_index: int | None = None,
    limit: int | None = None,
) -> Iterator[Snapshot]:
    """
    Loads snapshots from the FITS file where each HDU stores binary table with one timestamp.

    Supports condition on snapshot index and limit.
    """
    hdul = fits.open(filename, memmap=False)

    i = 0
    number = 0

    table: BinTableHDU
    for table in hdul:
        # skipping first HDU; it is required by the FITS specification.
        if i == 0:
            i += 1
            continue

        number_of_particles = len(table.data[list(fields.keys())[0]])

        timestamp = table.header["TIME"] | units.Myr
        # TODO: read units from TIME_UNIT if this entry exists, if not, use Myr
        particles = Particles(number_of_particles)

        for (key, val) in fields.items():
            if val is not None:
                setattr(particles, key, table.data[key] | val)
            else:
                try:
                    data = np.array(table.data[key], dtype=np.float64)
                except KeyError:
                    continue
                setattr(particles, key, data)

        if (snapshot_index is not None and i == snapshot_index) or snapshot_index is None:
            number += 1
            yield Snapshot(particles=particles, timestamp=timestamp)
            del particles
            del table
            gc.collect()

            if limit is not None and number >= limit:
                break

        i += 1

    hdul.close()


def from_logged_csvs(filenames: list[str], delimiter: str = ",") -> Iterator["Snapshot"]:
    """
    Loads snapshots from csv file in the following form: T,x,y,z,vx,vy,vz

    Implementation is not lazy, iterators exist only for the convinience.
    """
    tables = [
        pd.read_csv(filename, delimiter=delimiter, index_col=False).iterrows()
        for filename in filenames
    ]

    for rows in zip(*tables):
        rows = [row for (_, row) in rows]

        particles = Particles()

        for row in rows:
            particle = Particle()
            # TODO: need to use fields dict
            particle.position = [row["x"], row["y"], row["z"]] | units.kpc
            particle.velocity = [row["vx"], row["vy"], row["vz"]] | units.kms
            particle.mass = row["m"] | units.MSun
            particle.is_barion = 1

            particles.add_particle(particle)

        yield Snapshot(particles=particles, timestamp=rows[0]["T"] | units.Myr)
