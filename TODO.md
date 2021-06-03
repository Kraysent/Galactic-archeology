## Nearest future:
* Add integrator for NEMO integration
* Add console progress bar during integration (not sure how it should work though. Probably it should use some kind of event system: it subscribes to event in ```AbstractIntegrator``` and then it is instantiated during every dump of data (see point below))
* Create event system for ```AbstractIntegrator```. In more detail: move integration ```while``` loop to new method of ```AbstractIntegrator```. To track parameters it should use event system: ```AbstractIntegrator``` has attribute that stores the list of methods. If I want specific method to run every step of integration, I would add it to this list (subscribe) and then in every step of integration ```AbstractIntegrator``` iterates over all subscribers and calls them. 

## More distant future:
* Create abstract class for creation of the systems. Probably it should be separate from ```SystemFactory``` and just provide sets of particles for it.