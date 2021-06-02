from abc import abstractmethod
from amuse.lab import ScalarQuantity

class AbstractIntegrator:
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def evolve_model(self, time: ScalarQuantity):
        pass

    @property
    @abstractmethod
    def model_time(self) -> ScalarQuantity:
        pass
