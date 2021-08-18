from amuse.datamodel.particles import Particles
from amuse.lab import units
from archeology.datamodel import Snapshot
from astropy.io import fits
from astropy.io.fits.hdu.table import BinTableHDU


class FITSWriteManager:
    def __init__(self, filename: str) -> None:
        self.fields = {
            'x': units.kpc, 'y': units.kpc, 'z': units.kpc,
            'vx': units.kms, 'vy': units.kms, 'vz': units.kms,
            'mass': units.MSun
        }
        self.filename = filename

    def write_data(self, snapshot: Snapshot):
        cols = []

        for (key, val) in self.fields.items():
            col = fits.Column(
                name = key, 
                unit = str(self.fields[key]), 
                format = 'E', 
                array = getattr(snapshot.particles, key).value_in(val)
            )
            cols.append(col)

        cols = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(cols)
        hdu.header['TIME'] = snapshot.timestamp.value_in(units.Myr)
        hdu.writeto(self.filename, overwrite = True)

    def append_data(self, snapshot: Snapshot):
        cols = []

        for (key, val) in self.fields.items():
            col = fits.Column(
                name = key, 
                unit = str(self.fields[key]), 
                format = 'E', 
                array = getattr(snapshot.particles, key).value_in(val)
            )
            cols.append(col)

        cols = fits.ColDefs(cols)
        hdu = fits.BinTableHDU.from_columns(cols)
        hdu.header['TIME'] = snapshot.timestamp.value_in(units.Myr)

        try:
            fits.append(self.filename, hdu.data, hdu.header)
            # hdul = fits.open(self.filename, memmap = True)
            # hdul.append(hdu)
            # hdul.writeto(self.filename, overwrite = True)
        except:
            hdu.writeto(self.filename, overwrite = True)

class FITSReadManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.fields = {
                'x': units.kpc, 'y': units.kpc, 'z': units.kpc,
                'vx': units.kms, 'vy': units.kms, 'vz': units.kms,
                'mass': units.MSun
            }
        self.frame = -1
        self.hdul = fits.open(self.filename, memmap = True)

    def read_data(self) -> Snapshot:
        snapshot = Snapshot(Particles, 0 | units.Myr)

        table: BinTableHDU = self.hdul[self.frame + 1]

        snapshot.timestamp = table.header['TIME'] | units.Myr
        number_of_particles = len(table.data[list(self.fields.keys())[0]])
        snapshot.particles = Particles(number_of_particles)

        for (key, val) in self.fields.items():
            setattr(snapshot.particles, key, table.data[key] | val)

        return snapshot

    def next_frame(self) -> bool:
        if self.frame < len(self.hdul) - 2:
            self.frame += 1
            return True
        else: 
            self.hdul.close()
            return False
