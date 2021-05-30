import numpy as np
from amuse.lab import units
from pandas import DataFrame


class Tracker:
    def __init__(self, integrator):
        self.integrator = integrator
        # this probably should be a multiindex pandas dataframe
        # but it is quite a complex thing to do right now;
        # also i am not sure about its efficiency during append.
        # Though ndarray is not efficient either
        self.data = np.zeros(shape = (0, 7, len(integrator.particles)))
        self.common_parameters = DataFrame.from_dict({
            'T': []
        })

    def track_parameters(self):
        new = np.zeros(shape = (1, 7, len(self.integrator.particles)))

        # Positions
        new[0][0] = self.integrator.particles.x.value_in(units.kpc)
        new[0][1] = self.integrator.particles.y.value_in(units.kpc)
        new[0][2] = self.integrator.particles.z.value_in(units.kpc)

        # Velocities
        new[0][3] = self.integrator.particles.vx.value_in(units.kms)
        new[0][4] = self.integrator.particles.vy.value_in(units.kms)
        new[0][5] = self.integrator.particles.vz.value_in(units.kms)

        # Masses
        new[0][6] = self.integrator.particles.mass.value_in(units.MSun)

        self.data = np.append(self.data, new, axis = 0)

        common_new = {
            'T': self.integrator.model_time.value_in(units.Myr)
        }
        self.common_parameters = self.common_parameters.append(common_new, ignore_index = True)

    def get_positions(self) -> np.ndarray:
        '''
        Returns positions of all particles over time: 
        
        get_positions().shape = (number_of_timesteps, number_of_dimensions, number_of_particles)
        '''
        return self.data[:, 0:3]

    def get_velocities(self) -> np.ndarray:
        '''
        Returns velocities of all particles over time

        get_velocities().shape = (number_of_timesteps, number_of_dimensions, number_of_particles)
        '''
        return self.data[:, 3:6]

    def get_masses(self) -> np.ndarray:
        '''
        Returns masses of all particles over time

        get_masses().shape = (number_of_timesteps, number_of_particles)
        '''
        return self.data[:, 6]

    def get_center_of_mass_position(self) -> np.ndarray:
        '''
        Return position of all particles over time

        get_center_of_mass_position().shape = (number_of_timesteps, number_of_dimensions)
        '''
        mass = self.get_masses()
        total_mass = mass.sum(axis = 1)
        pos = self.get_positions()

        cm_pos = (pos * mass[:, np.newaxis, :]).sum(axis = 2) / total_mass[:, np.newaxis]

        return cm_pos


    def get_common_parameters(self):
        return self.common_parameters
