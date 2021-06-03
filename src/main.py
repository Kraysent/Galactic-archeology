import numpy as np
from amuse.lab import units

from integrators.bhtree_amuse_integrator import BHTreeAMUSEIntegrator
from system_factory import *
from tracker import Tracker
from visualizer import Visualizer

N1 = 500
N2 = 250
max_time = 500 | units.Myr
# max_time = 3000 | units.Myr

factory = SystemFactory()
factory.add_system(SystemType.KING, 1e11 | units.MSun, 10. | units.kpc, N1)
factory.add_system(SystemType.KING, 5e10 | units.MSun, 5. | units.kpc, N2, vector_from_spherical(30 | units.kpc, 30 / 57.7, np.pi), [210, 0, 0] | units.kms)
particles = factory.get_system()

integrator = BHTreeAMUSEIntegrator(mass = particles.total_mass(), rscale = particles.virial_radius(), timestep = 3 | units.Myr, epsilon_squared = (0.05 | units.kpc) ** 2)
integrator.particles = particles
tracker = Tracker(integrator)

i = 0

def subscriber():
    if i % 10 == 0:
        print('{} Myr'.format(np.round(integrator.model_time.value_in(units.Myr))), end = ' | ')

    tracker.track_parameters()

integrator.subscribe(subscriber)

while integrator.model_time < max_time:
    integrator.evolve_model(integrator.timestep * i)
    i += 1

pos = tracker.get_positions()
vel = tracker.get_velocities()
cm_pos = tracker.get_center_of_mass_position()
cm_vel = tracker.get_center_of_mass_velocity()

params = tracker.get_common_parameters()
pow = np.array([8, 0, 0])[np.newaxis, :] + cm_pos
pow_vel = np.array([200, 0, 0])[np.newaxis, :] + cm_vel

v_r_length = tracker.get_radial_velocity(pow, pow_vel)
v_tau_length = tracker.get_tangential_velocity(pow, pow_vel)

visualizer = Visualizer((2, 5), [
    ((0, 0), 2, 2),
    ((0, 2), 2, 2),
    ((0, 4), 1, 1),
    ((1, 4), 1, 1)
])

visualizer.set_axs_lims([
    (-150, 150, -200, 200),
    (-150, 150, -200, 200),
    (0, 500, -250, 250),
    (-600, 500, 0, 500)
])
visualizer.set_axs_labels([
    ('x, kpc', 'y, kpc'),
    ('x, kpc', 'z, kpc'),
    ('v_xy, km/s', 'v_z, km/s'),
    ('v_r, km/s', 'v_tau, kms')
])

visualizer.set_data([
    (pos[:, 0], pos[:, 1]),
    (pos[:, 0], pos[:, 2]),
    ((vel[:, 0] ** 2 + vel[:, 1] ** 2) ** 0.5, vel[:, 2]),
    (v_r_length, v_tau_length)
], titles = ['Time: {} Myr'.format(np.round(t, 2)) for t in params['T']])

visualizer.animate(sep = N1, width = 1500, height = 900, dpi = 90, filename = 'output/animation.mp4')
