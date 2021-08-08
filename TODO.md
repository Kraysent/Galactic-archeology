# Model:
## Nearest future:
- Place heavy particles into the center of the galaxies.
- Explore the dependency of the merger time from the masses of black holes (with masses like 10, 20, 30 times of the real black hole) and extrapolate it to the actual masses (we cannot explore them directly because of mass resolution).

## More distant future: 
- Play with mass resolution of the models.
- Play with direction and distance of the infall of the satellite.

# Program: 
## Issues:
- For some unknown reason plane direction changes to opposite every once in a while

## Nearest future:
- Deal with the tree of abstract classes: do we really need abstractxyztask and abstractscattertask as its heir? 
- Add integration to the primary program.
- Implement pyfalcon integration to the integrator module of the program (and than track several parameters more often then the output of gurfalcON).
- Create kind of time plot abstract class that has no options.
- Zoom in the central region during late stages of evolution.
- Add contour plots along with density ones

## More distant future:
- Add some kind of free parameters' space to the Snapshot class. Probably it should be made with PhaseSpace class that stores x, y, z, vx, vy, vz and some other parameters.
- Add tests for the code

# Thoughts:
- Probably for the models there should be some ModelBuilder class that implements Builder pattern to create models of the Milky Way (it should have methods like add_black_hole, add_layer(mass, extent), add_halo and so on).