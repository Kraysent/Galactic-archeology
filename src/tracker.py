import numpy as np
from amuse.lab import units
from pandas import DataFrame


class Tracker:
    def __init__(self, integrator):
        self.integrator = integrator
        # this should probably be a multiindex pandas dataframe
        # but it is quite a complex thing
        # also i am not sure about its efficiency during append.
        # Though ndarray is not efficient either
        self.data = np.zeros(shape = (0, 6, len(integrator.particles)))
        self.common_parameters = DataFrame.from_dict({
            'T': [],
            'cmx': [],
            'cmy': [],
            'cmz': []
        })

    def track_parameters(self):
        new = np.zeros(shape = (1, 6, len(self.integrator.particles)))
        new[0][0] = self.integrator.particles.x.value_in(units.kpc)
        new[0][1] = self.integrator.particles.y.value_in(units.kpc)
        new[0][2] = self.integrator.particles.z.value_in(units.kpc)
        new[0][3] = self.integrator.particles.vx.value_in(units.kms)
        new[0][4] = self.integrator.particles.vy.value_in(units.kms)
        new[0][5] = self.integrator.particles.vz.value_in(units.kms)
        self.data = np.append(self.data, new, axis = 0)

        common_new = {
            'T': self.integrator.model_time.value_in(units.Myr),
            'cmx': self.integrator.particles.center_of_mass().x.value_in(units.kpc),
            'cmy': self.integrator.particles.center_of_mass().y.value_in(units.kpc),
            'cmz': self.integrator.particles.center_of_mass().z.value_in(units.kpc)
        }
        self.common_parameters = self.common_parameters.append(common_new, ignore_index = True)

    def get_positions(self):
        return self.data[:, 0:3]

    def get_velocities(self):
        return self.data[:, 3:6]

    def get_common_parameters(self):
        return self.common_parameters
