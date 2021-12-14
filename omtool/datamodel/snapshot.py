from typing import Iterator, List
from amuse.datamodel.particles import Particle, Particles
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
        'mass': units.MSun, 
        'is_barion': None
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
            array = getattr(self.particles, key)
            fmt = 'L'

            if val is not None:
                array = array.value_in(val)
                fmt = 'E'

            col = fits.Column(
                name = key,
                unit = str(Snapshot.fields[key]), 
                format = fmt, 
                array = array
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
                if val is not None:
                    setattr(snapshot.particles, key, table.data[key] | val)
                else: 
                    data = np.array(table.data[key], dtype = np.float64)
                    setattr(snapshot.particles, key, data)

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
        table['barion'].map({ 'True': True, 'False': False })
        particles = Particles(len(table.iloc[:, 0]))
        particles.x = np.array(table['x']) | units.kpc
        particles.y = np.array(table['y']) | units.kpc
        particles.z = np.array(table['z']) | units.kpc
        particles.vx = np.array(table['vx']) | units.kms
        particles.vy = np.array(table['vy']) | units.kms
        particles.vz = np.array(table['vz']) | units.kms
        particles.mass = np.array(table['m']) | 232500 * units.MSun
        particles.is_barion = table['barion']

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot

    @staticmethod
    def from_logged_csvs(filenames: List[str], delimiter: str = ',') -> Iterator['Snapshot']:
        # This is not lazy implementation!
        tables = []

        for filename in filenames:
            tables.append(pandas.read_csv(filename, delimiter = delimiter, index_col = False))
            
        tables = [table.iterrows() for table in tables]

        for rows in zip(*tables):
            rows = [row for (_, row) in rows]

            particles = Particles()

            for row in rows:
                particle = Particle()
                particle.position = [row['x'], row['y'], row['z']] | units.kpc
                particle.velocity = [row['vx'], row['vy'], row['vz']] | units.kms
                particle.mass = row['m'] | units.MSun
                particle.is_barion = 1

                particles.add_particle(particle)

            yield Snapshot(particles, rows[0]['T'] | units.Myr)
            
    # shouldn't this method be static?
    def from_mass(mass: ScalarQuantity) -> 'Snapshot':
        particles = Particles(1)
        particles[0].position = [0, 0, 0] | units.kpc
        particles[0].velocity = [0, 0, 0] | units.kms
        particles[0].mass = mass
        particles[0].is_barion = True

        snapshot = Snapshot(particles, 0 | units.Myr)

        return snapshot
        