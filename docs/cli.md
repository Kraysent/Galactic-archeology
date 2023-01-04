# Command Line Interface

## `create`

### Usage

```bash
omtool create <path>
```

* `path`: `string` - path to YAML configuration file. 

### Description

Implements model creation functionality. All it does is calling of `create()` function with configuration loaded from YAML configuration file. For longer description see [its documentation](creation.md).

## `integrate`

### Usage

```bash
omtool integrate <path>
```

* `path`: `string` - path to YAML configuration file. 

### Description

Implements model integration functionality. All it does is calling of `integrate()` function with configuration loaded from YAML configuration file.

## `analize`

### Usage

```bash
omtool analize <path>
```

* `path`: `string` - path to YAML configuration file. 

### Description

Implements model analysis functionality. All it does is calling of `analize()` function with configuration loaded from YAML configuration file.

## `generate-schema`

### Usage

```bash
omtool generate-schema
```

### Description

This command is usually needed after the changes in configuration file structure of any previous commands. It regenerates JSON schemas for these configuration files. 

## `export-csv`

### Usage

```bash
omtool export-csv <fits-path> <snapshot-number>
```

* `fits-path`: `string` - path to file with the FITS model.
* `snapshot-number`: `integer` - index (starting from 0) of a snapshot of interest inside this file.

### Description

Extracts snapshot from HDU of given FITS file and exports it into CSV.
