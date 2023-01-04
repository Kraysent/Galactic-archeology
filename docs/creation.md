# Creation

## Basics

Creation mode is the first one you might encounter. Its logic is simple: take a bunch of files and particle parameteres and create output file with all of them.

Basic creation configuration file can be found [here](https://github.com/Kraysent/OMTool/blob/main/examples/full_model/creation_config.yaml). It looks like this:

```yaml
output_file: !env "{WORKING_DIR}/test.fits"
overwrite: True

logging:
  level: debug
  filename: !env "{WORKING_DIR}/test_json_log.txt"

objects:
  - name: body
    args:
      mass: !q [4.e+8, MSun]
    position: !q [[0, 0, 0], kpc]
    velocity: !q [[0, 0, 0], kms]
  - name: csv
    args:
      delimiter: " "
      path: !env "{DATA_DIR}/host.csv"
    position: !q [[0, 0, 0], kpc]
    velocity: !q [[0, 0, 0], kms]
  - name: body
    args:
      mass: !q [1.e+8, MSun]
    position: !q [[20, 0, 0], kpc]
    velocity: !q [[0, 100, 0], kms]
  - name: csv
    args:
      delimiter: " "
      path: !env "{DATA_DIR}/sat.csv"
    position: !q [[20, 0, 0], kpc]
    velocity: !q [[0, 100, 0], kms]
```

Let's go line-by-line:

```yaml
output_file: !env "{WORKING_DIR}/test.fits"
```

Resulting file would be written into the `test.fits` in the path `$WORKING_DIR`. `!env` tag tells the program to look at the string and paste environment variables into it.

```yaml
overwrite: True
```

If file already exists, overwrite it. By default this option is `False`.

```yaml
logging:
  level: debug
  filename: !env "{WORKING_DIR}/test_json_log.txt"
```

These are logging parameters. `level` is, of course, the minimum level of the logging. By default is `INFO`, this should be enough for simple calculations. `filename` is optional parameter that specifies where to write logs. By default, they are written into the `stdout` in pretty format. If you specify filename, it would duplicate output there; each line written is valid JSON. This makes it ideal for machine-reading if you want to track some parameters during the creation (or integration, or analysis).

```yaml
objects:
  ....
```

This field lists models that would be composed into single file from the `output_file` option. More on models in the [separate section](#models).

You can customize imported models using `imports` statement. Example:

```yaml
imports:
  models:
    - path/to/first/model.py
    - path/to/second/model.py
```

Note that if you specify other imports, default ones are omitted. You should import them separately in this case (glob syntax is supported):

```yaml
imports:
  models:
    - path/to/first/model.py
    - path/to/second/model.py
    - !env {OMTOOL_DIR}/tools/models/*
```

## Models

Model is the basic component of the creation configuration. This section
describes how to use models in configuration files, not how to create
them.

```yaml
- name: body
  args:
    mass: !q [4.e+8, MSun]
  position: !q [[0, 0, 0], kpc]
  velocity: !q [[0, 0, 0], kms]
  # downsample_to: 1
```

New object may be created with these arguments:

-  `name` (`str`): name of the plugin with the model.
-  `args` (`dict`): arguments that would be passed into constructor. For example, single body constructor needs only the mass (`!q` tag denotes quantity).
-  `position` (`VectorQuantity`): initial offset of the object. Zero vector by default.
-  `velocity` (`VectorQuantity`): initial velocity of the object. Zero vector by default.
-  `downsample_to` (`int`): if model has more particles, than you need, you may downsample it to specified number.

By default there are several built-in plugins with the models. They are stored inside the [tools](https://github.com/Kraysent/OMTool/tree/main/tools/models) directory of the project. Their arguments can be found in the constructors.

### Example

Let's examine example from above (added downscale for educational
purposes):

```yaml
objects:
  # Create one body at index 1 with mass 4 * 10^8 MSun at the origin.
  - name: body
    args:
      mass: !q [4.e+8, MSun]
    position: !q [[0, 0, 0], kpc]
    velocity: !q [[0, 0, 0], kms]
  # Load system of particles from $DATA_DIR/host.csv file and put all of them at the origin.
  - name: csv
    args:
      delimiter: " "
      path: !env "{DATA_DIR}/host.csv"
    position: !q [[0, 0, 0], kpc]
    velocity: !q [[0, 0, 0], kms]
  # Load single particle with mass 10^8 MSun and put it 20 kpc away from the origin and give 
  #  it orthogonal initial velocity 180 km/s. Also, take random subset of 100k particles from it 
  #  and use it instead but scale all of the masses by factor initial_length / 100000.
  - name: body
    args:
      mass: !q [1.e+8, MSun]
    position: !q [[20, 0, 0], kpc]
    velocity: !q [[0, 100, 0], kms]
    downscale_to: 100000
  # Load system of particles from $DATA_DIR/sat.csv file and add 20 kpc to all of their x 
  #  coordinates and 100 km/s to their y velocity coordinate.
  - name: csv
    args:
      delimiter: " "
      path: !env "{DATA_DIR}/sat.csv"
    position: !q [[20, 0, 0], kpc]
    velocity: !q [[0, 100, 0], kms]
```
