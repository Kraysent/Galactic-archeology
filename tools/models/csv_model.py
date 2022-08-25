import numpy as np
import pandas
from amuse.lab import Particles, units

from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="csv")
class CSVModel(AbstractModel):
    def __init__(self, path: str, delimiter: str):
        self.path = path
        self.delimiter = delimiter

    def run(self) -> Snapshot:
        """
        Read the list of particles from the CSV file on form
        x,y,z,vx,vy,vz,m,is_barion
        """
        table = pandas.read_csv(self.path, delimiter=self.delimiter, index_col=False)
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

        return Snapshot(particles, 0 | units.Myr)
