from archeology.analysis.visual.nbody_object import NbodyObject
from archeology.analysis.tasks import MassProfileTask
from archeology.datamodel.snapshot import Snapshot
from scipy import interpolate, misc, integrate
import numpy as np
import matplotlib.pyplot as plt
from amuse.lab import units, constants

def manual_analize():
    sigma = 100 | units.kms
    R = 10 | units.kpc
    G = constants.G
    m_sat = 1e7 | units.MSun
    b_max = 300 | units.kpc
    b_min = 1 | units.AU
    ln_lambda = np.log(b_max / b_min)

    def t(r):
        return (sigma * r ** 2) / (np.sqrt(2) * G * m_sat * ln_lambda) 

    T = t(R)
    
    print(T.value_in(units.Gyr))