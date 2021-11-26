from typing import Iterator
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity
from astropy.io import fits
from astropy.io.fits.hdu.table import BinTableHDU
import pandas
import numpy as np


class Snapshot:
    fields = {
        'x': units.kpc, 'y': units.kpc, 'z': units.kpc,
        'vx': units.kms, 'vy': units.kms, 'vz': units.kms,
        'mass': units.MSun
    }
    
    def __init__(self, 
        particles: Particles = Particles(), 
        timestamp: ScalarQuantity = 0 | units.Myr
    ):
        self.particles = particles
        self.timestamp = timestamp

    def __getitem__(self, value) -> 'Snapshot':
        return Snapshot(self.particles[value], self.timestamp)

    def __add__(self, other: 'Snapshot') -> 'Snapshot':
        if self.timestamp == other.timestamp:
            particles = Particles()
            particles.add_particles(self.particles)
            particles.add_particles(other.particles)

            return Snapshot(particles, self.timestamp)
        else:
            raise RuntimeError('Tried to sum snapshots with different timestamps.')

    def add(self, other: 'Snapshot', ignore_timestamp = False):
        '''
        Adds other snapshot to this one. If ignore_timestamps is False, 
        does not change timestamp. Otherwise RuntimeError would be thrown if 
        timestamps are different.
        '''
        if not ignore_timestamp and (self.timestamp != other.timestamp):
            raise RuntimeError('Tried to sum snapshots with different timestamps.')

        self.particles.add_particles(other.particles)

    @staticmethod
    def file_info(filename: str) -> int:
        '''
        Returns number of snapshots in the FITS file.
        '''
        hdul = fits.open(filename, memmap = True)
        
        number_of_snaps = len(hdul) - 1

        hdul.close()

        return number_of_snaps

    def to_fits(self, filename: str, append: bool = False):
        cols = []

        for (key, val) in Snapshot.fields.items():
            col = fits.Column(
                name = key,
                unit = str(Snapshot.fields[key]), 
                format = 'E', 
                array = getattr(self.particles, key).value_in(val)
            )
            cols.append(col)

        cols = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(cols)
        hdu.header['TIME'] = self.timestamp.value_in(units.Myr)

        if append:
            try:
                fits.append(filename, hdu.data, hdu.header)
            except:
                hdu.writeto(filename, overwrite = True)
        else:
            hdu.writeto(filename, overwrite = True)

    @staticmethod
    def from_fits(filename: str) -> Iterator['Snapshot']:
        hdul = fits.open(filename, memmap = True)
        snapshot = Snapshot(Particles, 0 | units.Myr)

        for frame in range(len(hdul) - 1):
            table: BinTableHDU = hdul[frame + 1]
            number_of_particles = len(table.data[list(Snapshot.fields.keys())[0]])

            snapshot.timestamp = table.header['TIME'] | units.Myr
            snapshot.particles = Particles(number_of_particles)

            for (key, val) in Snapshot.fields.items():
                setattr(snapshot.particles, key, table.data[key] | val)

            yield snapshot

    @staticmethod
    def from_fits_frame(filename: str, frame: int = 0) -> 'Snapshot':
        hdul = fits.open(filename, memmap = True)
        snapshot = Snapshot(Particles, 0 | units.Myr)

        table: BinTableHDU = hdul[frame + 1]

        snapshot.timestamp = table.header['TIME'] | units.Myr
        number_of_particles = len(table.data[list(Snapshot.fields.keys())[0]])
        snapshot.particles = Particles(number_of_particles)

        for (key, val) in Snapshot.fields.items():
            setattr(snapshot.particles, key, table.data[key] | val)

        return snapshot

    @staticmethod
    def from_csv(filename: str, delimiter: str = ',') -> 'Snapshot':
        table = pandas.read_csv(filename, delimiter = delimiter, index_col = False)
        particles = Particles(len(table.iloc[:, 0]))
        particles.x = np.array(table['x']) | units.kpc
        particles.y = np.array(table['y']) | units.kpc
        particles.z = np.array(table['z']) | units.kpc
        particles.vx = np.array(table['vx']) | units.kms
        particles.vy = np.array(table['vy']) | units.kms
        particles.vz = np.array(table['vz']) | units.kms
        particles.mass = np.array(table['m']) | 232500 * units.MSun

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot

    def from_mass(mass: ScalarQuantity) -> 'Snapshot':
        particles = Particles(1)
        particles.x = np.array([0]) | units.kpc
        particles.y = np.array([0]) | units.kpc
        particles.z = np.array([0]) | units.kpc
        particles.vx = np.array([0]) | units.kms
        particles.vy = np.array([0]) | units.kms
        particles.vz = np.array([0]) | units.kms
        particles.mass = np.array([mass.value_in(units.MSun)]) | units.MSun

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot
        