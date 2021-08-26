## Model:
### Nearest future:
- Place heavy particles into the center of the galaxies.
- Explore the dependency of the merger time on the masses of black holes (with masses like 10, 20, 30 times of the real black hole) and extrapolate it to the actual masses (we cannot explore them directly because of mass resolution).

### More distant future: 
- Play with mass resolution of the models.
- Play with direction and distance of the infall of the satellite.

## Program: 
### Issues:
- For some unknown reason plane direction changes to opposite every once in a while

### Nearest future:
- Deal with the tree of abstract classes: do we really need abstractxyztask and abstractscattertask as its heir? 
- Create kind of time plot abstract class that has no options.
- Zoom in the central region during late stages of evolution.
- Add contour plots along with density ones.
- Swap AbstractXYZTask with AbstractPlaneTask (or just method in abstracttask?) that can project data on any plane. 
- Clean up DrawParameters. There are probably some unnecessary fields.

### More distant future:
- Add some kind of free parameters' space to the Snapshot class. Probably it should be made with PhaseSpace class that stores x, y, z, vx, vy, vz and some other parameters.
- Add tests for the code.

## Thoughts:
### Models:
Probably for the models there should be some ModelBuilder class that implements Builder pattern to create models of the Milky Way (it should have methods like add_black_hole, add_layer(mass, extent), add_halo and so on).

### Zooming:
Zooming to the central region should be implemented using some kind of evolution of plot parameters over time. Possibly that will require moving plot parameters back to main while loop. Viable approach could be to implement observer pattern to the task class and invoke observers only when task needs zooming or smth. Though this would break single-responsibility principle (so the task would know smth about the view). 

Another possible solution is to create some middle class that takes task (or its output) and creates layout settings for Visualizer. This class should store the task itself, drawing logic and it might have the logic to change plot behaviour. The problem is that there might be several tasks that use one axes so there might be an ambiguity when changing parameters of the plot. 

Third approach is to create separate class that tracks some parameters (which?) of the tasks in given plot and changes plot layout according to some (which?) logic. That is some kind of Task but for plot itself. It might accept list of tasks for given axes (should it?) and snapshot in run method and change plot layout based on the parameters of the system.
Or it might accept just the snapshot and do something based on it. The drawback is that it might lead to code duplication during some computations.
