from archeology.analysis.visual.nbody_object import NbodyObject
from archeology.analysis.tasks import MassProfileTask
from archeology.datamodel.snapshot import Snapshot
from scipy import interpolate, misc, integrate
import numpy as np
import matplotlib.pyplot as plt

def manual_analize(datadir):
    filename = f'{datadir}/models/bh_1_0_out.fits'
    task = MassProfileTask()
    host_obj = NbodyObject(slice(1000001))
    sat_bh_mass = 1e7 / 232500
    sat_bh_rad = 150
    particle_mass = 2e6 / 232500

    snapshot = next(Snapshot.from_fits(filename))
    task.update_center(snapshot[host_obj.part].particles.center_of_mass())
    (rad, m) = task.run(snapshot[host_obj.part])
    m = m / 232500
 
    mass_func = interpolate.interp1d(rad, m, fill_value="extrapolate")

    def mass_func_der(x):
        return misc.derivative(mass_func, x, 0.01)

    plt.xlim(0, 100)
    plt.plot(rad, mass_func(rad))
    plt.show()

    def f(r):
        M = mass_func(r)
        M_prime = mass_func_der(r)

        return - 1 / (2 * sat_bh_mass) * ((M_prime * r - M) * M ** 0.5) / (np.log(1 + particle_mass / sat_bh_mass) * M_prime * r ** 0.5)

    res = integrate.quad(f, 0, sat_bh_rad)
    print(res)
    