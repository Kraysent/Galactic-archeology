from typing import Iterator, Tuple

from amuse.lab import Particles, ScalarQuantity

import io_service.readers as readers
from io_service.config import Config


class InputService:
    def __init__(self, config: Config) -> None:
        self.config = config
        
    def get_snapshot_generator(self) -> Iterator[Tuple[Particles, ScalarQuantity]]:
        if self.config.format == 'fits':
            if len(self.config.filenames) > 1:
                raise NotImplementedError('Reading of nmultiple FITS file at once is not implemented yet.')

            return readers.from_fits(self.config.filenames[0])
        elif self.config.format == 'csv':
            return readers.from_logged_csvs(self.config.filenames)

    def get_number_of_snapshots(self) -> int:
        if self.config.format == 'fits':
            if len(self.config.filenames) > 1:
                raise NotImplementedError('Reading of nmultiple FITS file at once is not implemented yet.')

            return readers.fits_file_info(self.config.filenames[0])
        elif self.config.format == 'csv':
            raise NotImplementedError('Length of list of csv snapshots is not implemented yet.')
