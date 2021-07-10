## Nearest future:
* Add console progress bar during integration.
* Add several colors for ```Visualizer``` class. ```animate``` method should take arguments that define separation between them.
* ```Tracker``` should store data on the hard drive. Reasons: 1. after certain point simulations might be too big to store them in RAM. 2. There would be an ability to reanalize data. 
* Add an option to plot only particles within some region of observation point.

    *There should be some beatiful way to provide only particles within some region of given position to ```Visualizer```. Probably I should somehow modify ```Tracker``` class. One approach is to provide special ```radius``` and ```pow``` parameters for each method and force them to use it.*

    *Also it would be cool to provide some lambda experession to each method and return needed things (velocities, cms, etc.) only for particles that obey this condition. This would be much more versatile.*
* Store ```Particle``` (probably AMUSE's native) structure in ```Tracker``` class. But it would need some faster iteration over it than the usual python's for loop (probably).

## More distant future:
* Create abstract class for creation of the systems. Probably it should be separate from ```SystemFactory``` and just provide sets of particles for it.
* Add integrator for NEMO integration.
* Potentially change parameters like x, y, z, vx, vy, vz, m to single PhaseSpace parameter (probably some interface or class at least)