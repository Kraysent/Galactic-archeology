# Model:
## Nearest future:
- Add heavy particle in the center.

## More distant future: 
- Play with mass resolution of the models.
- Play with direction and distance of the infall of the satellite

# Program: 
## Issues:
- For some reason plane direction changes to opposite every once in a while

## Nearest future:
- Deal with the tree of abstract classes: do we really need abstractxyztask and abstractscattertask as its heir? 
- Add integration to the primary program.
- Implement pyfalcon integration to the integrator module of the program (and than track several parameters more often then the output of gurfalcON).
- Create kind of time plot abstract class that has no options.
- Zoom in the central region during late stages of evolution.
- Add projection of the coordinates onto the host plane.

## More distant future:
- Add some kind of free parameters' space to the Snapshot class. Probably it should be made with PhaseSpace class that stores x, y, z, vx, vy, vz and some other parameters.
- Add tests for the code