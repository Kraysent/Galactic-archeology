from typing import Iterator

from omtool.core import datamodel
from omtool.core.configs import InputConfig
from omtool.core.datamodel import Snapshot


def initialize_input_snapshot(config: InputConfig) -> Iterator[Snapshot]:
    """
    Loads the snapshot from the file and adds an ability to read next snapshot.
    Implementation is lazy.
    """
    if config.format == "fits":
        if len(config.filenames) > 1:
            raise NotImplementedError(
                "Reading of multiple FITS files at once is not implemented yet."
            )

        return datamodel.from_fits(config.filenames[0])
    elif config.format == "csv":
        return datamodel.from_logged_csvs(config.filenames)
    else:
        raise RuntimeError(f'Unknown format of the file: "{config.format}"')
