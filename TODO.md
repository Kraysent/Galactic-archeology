## Nearest future:
* Add integrator for NEMO integration
* Add console progress bar during integration (not sure how it should work though. Probably it should use some kind of event system: it subscribes to event in ```AbstractIntegrator``` and then it is instantiated during every dump of data (see point below))
* Move integration ```while``` loop to specific method of ```AbstractIntegrator```.  
## More distant future:
* Create abstract class for creation of the systems. Probably it should be separate from ```SystemFactory``` and just provide sets of particles for it.