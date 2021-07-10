from amuse.units.core import named_unit
from amuse.units.quantities import ScalarQuantity
import numpy as np
from amuse.lab import units
from pandas import DataFrame
from amuse.io import read_set_from_file, write_set_to_file
import os

from integrators.abstract_integrator import AbstractIntegrator


class Tracker:
    def __init__(self, integrator: AbstractIntegrator, output_directory_name: str):
        self.integrator = integrator
        self.directory_name = output_directory_name
        self.common_parameters = DataFrame.from_dict({
            'T': []
        })

    def track_parameters(self):
        directory = self.directory_name
        filename = '{}.dat'.format(np.round(self.integrator.model_time.value_in(units.Myr), 2))
        write_set_to_file(self.integrator.particles, '{}/{}'.format(directory, filename))

    def _get_time_from_filename(filename: str, unit: named_unit) -> ScalarQuantity:
        filename = os.path.basename(filename)
        time = os.path.splitext(filename)[0]
        result = time | unit

        return result

    def _setup_datastruct_to_read(list_of_files: list, fields: list) -> dict:
        output = {}
        
        for filename in list_of_files: 
            curr_time = Tracker._get_time_from_filename(filename, units.Myr)
            output[curr_time] = {}

            for field in fields:
                output[curr_time][field] = []

        return output
        
    def read_fields(directory_name: str, fields: list, extension: str = 'dat') -> dict:
        # this method reads all the files with all the snapshots and take out fields 
        # it returns sorted dictionary, where keys are times and values 
        # are dicts {field_name: list_of_particles}
        filenames = []
        for root, _, files in os.walk('{}/'.format(directory_name)):
            for file in files:
                filenames.append(os.path.join(root, file))

        output = Tracker._setup_datastruct_to_read(files, fields)

        for filename in filenames:
            curr_particles = read_set_from_file(filename)
            curr_time = Tracker._get_time_from_filename(filename, units.Myr)

            for field in fields:
                output[curr_time][field] = getattr(curr_particles, field)

        return output

    # def get_common_parameters(self):
    #     return self.common_parameters

    # def get_number_of_timestamps(self):
    #     return len(self.common_parameters['T'])

    # def get_positions(self) -> np.ndarray:
    #     '''
    #     Returns positions of all particles over time: 
        
    #     get_positions().shape = (number_of_timesteps, number_of_dimensions, number_of_particles)
    #     '''
    #     return self.data[:, 0:3]

    # def get_velocities(self) -> np.ndarray:
    #     '''
    #     Returns velocities of all particles over time

    #     get_velocities().shape = (number_of_timesteps, number_of_dimensions, number_of_particles)
    #     '''
    #     return self.data[:, 3:6]

    # def get_masses(self) -> np.ndarray:
    #     '''
    #     Returns masses of all particles over time

    #     get_masses().shape = (number_of_timesteps, number_of_particles)
    #     '''
    #     return self.data[:, 6]

    # def get_center_of_mass_position(self) -> np.ndarray:
    #     '''
    #     Returns position of all particles over time

    #     get_center_of_mass_position().shape = (number_of_timesteps, number_of_dimensions)
    #     '''
    #     mass = self.get_masses()
    #     total_mass = mass.sum(axis = 1)
    #     pos = self.get_positions()

    #     cm_pos = (pos * mass[:, np.newaxis, :]).sum(axis = 2) / total_mass[:, np.newaxis]

    #     return cm_pos

    # def get_center_of_mass_velocity(self) -> np.ndarray:
    #     '''
    #     Returns velocity of center of mass over time

    #     get_center_of_mass_velocity().shape = (number_of_timesteps, number_of_dimensions)
    #     '''
    #     mass = self.get_masses()
    #     total_mass = mass.sum(axis = 1)
    #     vel = self.get_velocities()

    #     cm_vel = (vel * mass[:, np.newaxis, :]).sum(axis = 2) / total_mass[:, np.newaxis]

    #     return cm_vel

    # def get_radial_velocity(self, pow: np.ndarray, pow_vel: np.ndarray) -> np.ndarray:
    #     '''
    #     - pow - point of view radius vector, pow.shape = (number_of_timesteps, number_of_dimensions)
    #     - pow_vel - velocity vector of point of view, pow_vel.shape = (number_of_timesteps, number_of_dimensions)
        
    #     Returns signed absolute value of radial velocity of each particle from given point of view

    #     get_radial_velocity().shape = (number_of_timesteps, number_of_particles)
    #     '''
    #     if (pow.shape != (self.get_number_of_timesteps(), 3)):
    #         raise Exception("Point of view radius vector should have shape (number_of_timesteps, number_of_dimensions).")

    #     if (pow_vel.shape != (self.get_number_of_timesteps(), 3)):
    #         raise Exception("Point of view velocity vector should have shape (number_of_timesteps, number_of_dimensions).")

    #     r = self.get_positions() - pow[:, :, np.newaxis]
    #     v = self.get_velocities() - pow_vel[:, :, np.newaxis]

    #     r_len = (r ** 2).sum(axis = 1) ** 0.5
    #     e_r = r / r_len[:, np.newaxis, :]

    #     return (v * e_r).sum(axis = 1)

    # def get_tangential_velocity(self, pow: np.ndarray, pow_vel: np.ndarray) -> np.ndarray:
    #     '''
    #     - pow - point of view radius vector, pow.shape = (number_of_timesteps, number_of_dimensions)
    #     - pow_vel - velocity vector of point of view, pow_vel.shape = (number_of_timesteps, number_of_dimensions)
        
    #     Returns tangential velocity of each particle from given point of view

    #     get_tangential_velocity().shape = (number_of_timesteps, number_of_dimensions, number_of_particles)
    #     '''

    #     if (pow.shape != (self.get_number_of_timesteps(), 3)):
    #         raise Exception("Point of view radius vector should have shape (number_of_timesteps, number_of_dimensions).")

    #     if (pow_vel.shape != (self.get_number_of_timesteps(), 3)):
    #         raise Exception("Point of view velocity vector should have shape (number_of_timesteps, number_of_dimensions).")

    #     r = self.get_positions() - pow[:, :, np.newaxis]
    #     v = self.get_velocities() - pow_vel[:, :, np.newaxis]

    #     r_len = (r ** 2).sum(axis = 1) ** 0.5
    #     e_r = r / r_len[:, np.newaxis, :]

    #     v_r = (v * e_r).sum(axis = 1)[:, np.newaxis, :] * e_r

    #     return ((v - v_r) ** 2).sum(axis = 1) ** 0.5

