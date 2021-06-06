## Nearest future:
* Add integrator for NEMO integration.
* Add console progress bar during integration.
* Move integration ```while``` loop to specific method of ```AbstractIntegrator```.  
* Add several colors for ```Visualizer``` class. ```animate``` method should take arguments that define separation between them.
* Add an option to plot only particles within some region of observation point.

## More distant future:
* Create abstract class for creation of the systems. Probably it should be separate from ```SystemFactory``` and just provide sets of particles for it.