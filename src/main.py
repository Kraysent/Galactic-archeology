import numpy as np
from amuse.lab import units

from system_factory import *
from tracker import Tracker
from visualizer import Visualizer

N1 = 500
N2 = 250
max_time = 500 | units.Myr
# max_time = 3000 | units.Myr

factory = SystemFactory()
factory.add_system(GalaxyType.KING, 1e11 | units.MSun, 10. | units.kpc, N1)
factory.add_system(GalaxyType.KING, 5e10 | units.MSun, 5. | units.kpc, N2, vector_from_spherical(30 | units.kpc, 30 / 57.7, np.pi), [210, 0, 0] | units.kms)
factory.set_integrator(Integrator.BHTREE, 3 | units.Myr, (0.05 | units.kpc) ** 2)

integrator = factory.get_system()
tracker = Tracker(integrator)

i = 0

while integrator.model_time < max_time:
    integrator.evolve_model(integrator.parameters.timestep * i)
    i += 1

    tracker.track_parameters()

    if i % 10 == 0:
        new_var = print('{} Myr'.format(np.round(integrator.model_time.value_in(units.Myr))), end = ' | ')
        new_var

pos = tracker.get_positions()
vel = tracker.get_velocities()
mass = tracker.get_masses()
cm_pos = tracker.get_center_of_mass_position()

params = tracker.get_common_parameters()
pow = np.array([8, 0, 0])[np.newaxis, :] + cm_pos
velocity_of_pow = np.array([400, 0, 0])

# computing unit vector along vector from center of mass to each object
r = pos - pow[..., None]
r_len = np.sum(r ** 2, axis = 1) ** 0.5
er = r / np.expand_dims(r_len, axis = 1)

# computing radial velocity
v = vel - velocity_of_pow[..., None]
v_r_length = np.sum(v * er, axis = 1)
v_r = np.expand_dims(v_r_length, axis = 1) * er

#computing tangential velocity
v_tau = v - v_r
v_tau_length = np.sum(v_tau ** 2, axis = 1) ** 0.5

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
