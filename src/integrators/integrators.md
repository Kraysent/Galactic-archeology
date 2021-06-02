This is general description of classes in this submodule.

## ```IntegratorFactory``` class
It is used for creation of different AMUSE and NEMO integrators. 

## ```AbstractIntegrator``` class
This is abstract class that defines general properties of integrators. All other integrator classes should inherit from this one.

### ```__init__(self, **kwargs)```
* ```**kwargs``` - arguments specific to each integrator. For example, timestep can be used to specify timestep for all AMUSE integrators.

### ```evolve_model(self, time: ScalarQuantity)```
* ```time``` - time until which integration is performed

### Attributes:
* ```particles``` - use to get/set set of particles from/to integrator

### Properties:
* ```model_time``` - used to get current time of the system (either ```time``` parameter provided to last call of ```evolve_model``` or zero)

## BHTreeAMUSEIntegrator(AbstractIntegrator) class
This class implements ```AbstractIntegrator``` for Barnes-Hut tree code in AMUSE (```amuse.community.bhtree.interface.BHTree``` class)

