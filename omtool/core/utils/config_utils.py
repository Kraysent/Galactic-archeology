import os
import numpy as np
import yaml
from amuse.lab import ScalarQuantity, VectorQuantity, units
from amuse.units.core import named_unit


def str_to_unit(name: str) -> named_unit:
    """
    Converts string representation of the unit into named_unit object
    """
    unit_names = ["Myr", "kpc", "kms", "MSun", "J"]
    actual_units = [units.Myr, units.kpc, units.kms, units.MSun, units.J]

    index = unit_names.index(name) if name in unit_names else None

    if index is None:
        raise RuntimeError(f"{str} is unsupported unit name.")

    return actual_units[index]


def unit_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.Node
) -> ScalarQuantity | VectorQuantity:
    """
    Processes the !q tag
    """
    data = loader.construct_sequence(node, deep=True)

    if len(data) != 2:
        raise ValueError(f"Tried to cast {data} to quantity.")

    if isinstance(data[0], list):
        return np.array(data[0]) | str_to_unit(data[1])

    return data[0] | str_to_unit(data[1])


def env_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    """
    Processes the !env tag
    """
    data = loader.construct_scalar(node)

    if not isinstance(data, str):
        raise ValueError(f"Tried to paste environment variable into not-string: {data}")

    return data.format(**os.environ)


def slice_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> slice:
    """
    Processes the !slice tag
    """
    data = loader.construct_sequence(node)

    if len(data) == 1 or len(data) == 2 or len(data) == 3:
        return slice(*data)
    else:
        raise ValueError(
            f"{data} has len {len(data)} while 1, 2 or 3 is possible to construct a slice."
        )


def yaml_loader() -> yaml.SafeLoader:
    """
    Loader that processes all the tags.
    """
    loader = yaml.SafeLoader
    loader.add_constructor("!q", unit_constructor)
    loader.add_constructor("!env", env_constructor)
    loader.add_constructor("!slice", slice_constructor)

    return loader


def required_get(data: dict, field: str):
    """
    Tries to obtain the field from the dictionary and throws the
    error in case it was not found.
    """
    try:
        return data[field]
    except KeyError as ex:
        raise Exception(f"no required key {field} found") from ex
