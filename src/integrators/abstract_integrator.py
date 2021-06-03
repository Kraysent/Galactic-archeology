from abc import abstractmethod
from amuse.datamodel.particles import Particles
from amuse.lab import ScalarQuantity

class AbstractIntegrator:
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def evolve_model(self, time: ScalarQuantity):
        pass

    def subscribe(self, reciever):
        if not hasattr(self, '_subscribers'):
            self._subscribers = []

        self._subscribers.append(reciever)

    def _raise_subscribers(self):
        for f in self._subscribers:
            f()

    @property
    @abstractmethod
    def model_time(self) -> ScalarQuantity:
        pass

    @property
    @abstractmethod
    def particles(self) -> Particles:
        pass

    @particles.setter
    @abstractmethod
    def particles(self, value: Particles):
        pass
