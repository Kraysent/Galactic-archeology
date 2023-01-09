# Command Line Interface

```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  analize          Analize series of snapshots
  create           Create snapshot from config
  csv-export       Exports snapshot into CSV
  generate-schema  Generates JSON schema
  integrate        Evolve snapshot in time
```

## `create`

### Usage

```
Usage: main.py create [OPTIONS] CONFIG

  A way to convert YAML description of the system into the snapshot with actual particles.

  CONFIG is a path to creation configuration file.

Options:
  --help  Show this message and exit.

```

### Description

Implements model creation functionality. All it does is calling of `create()` function with configuration loaded from YAML configuration file. For longer description see [its documentation](creation.md).

## `integrate`

### Usage

```
Usage: main.py integrate [OPTIONS] CONFIG

  A way to evolve system over given period of time.

  CONFIG is a path to integration configuration file.

Options:
  --help  Show this message and exit.
```

### Description

Implements model integration functionality. All it does is calling of `integrate()` function with configuration loaded from YAML configuration file.

## `analize`

### Usage

```
Usage: main.py analize [OPTIONS] CONFIG

  A way to analize system after the evolution.

  CONFIG is a path to analysis configuration file.

Options:
  --help  Show this message and exit.

```

### Description

Implements model analysis functionality. All it does is calling of `analize()` function with configuration loaded from YAML configuration file.

## `generate-schema`

### Usage

```
Usage: main.py generate-schema [OPTIONS]

  Generates JSON schema for all of the configuration files.

Options:
  -c, --creation TEXT     Path where to save the creation schema to  [default:
                          cli/schemas/creation_schema.json]
  -i, --integration TEXT  Path where to save the integration schema to
                          [default: cli/schemas/integration_schema.json]
  -a, --analysis TEXT     Path where to save the analysis schema to  [default:
                          cli/schemas/analysis_schema.json]
  --help                  Show this message and exit.

```

### Description

This command is usually needed after the changes in configuration file structure of any previous commands. It regenerates JSON schemas for these configuration files. 

## `csv-export`

### Usage

```
Usage: main.py csv-export [OPTIONS]

  Export particular snapshot from FITS into CSV file.

Options:
  -i, --input-file TEXT   Path to input FITS file with snapshots.  [required]
  -o, --output-file TEXT  Path to output FITS file.  [required]
  -n, --index INTEGER     Index of snapshot inside input file.  [required]
  --help                  Show this message and exit.

```

### Description

Extracts snapshot from HDU of given FITS file and exports it into CSV.
