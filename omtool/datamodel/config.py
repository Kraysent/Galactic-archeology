import os
from typing import Union

import logger
import numpy as np
import yaml
from amuse.lab import ScalarQuantity, VectorQuantity, units
from amuse.units.core import named_unit


def str_to_unit(s: str) -> named_unit:
    unit_names = ['Myr', 'kpc', 'kms', 'MSun', 'J']
    actual_units = [units.Myr, units.kpc, units.kms, units.MSun, units.J]

    index = unit_names.index(s) if s in unit_names else None

    if index is not None:
        return actual_units[index]
    else:
        raise RuntimeError(f'{str} is unsupported unit name.')

def unit_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.Node
) -> Union[ScalarQuantity, VectorQuantity]:
    data = loader.construct_sequence(node, deep = True)

    if len(data) != 2:
        raise RuntimeError(f'Tried to cast {data} to quantity.')

    if isinstance(data[0], list):
        return np.array(data[0]) | str_to_unit(data[1])
    else:
        return data[0] | str_to_unit(data[1])

def env_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.Node
) -> str:
    data = loader.construct_scalar(node)

    if not isinstance(data, str):
        raise RuntimeError(f'Tried to paste environment variable into not-string: {data}')

    return data.format(**os.environ)

def yaml_loader() -> yaml.Loader:
    loader = yaml.SafeLoader
    loader.add_constructor('!q', unit_constructor)
    loader.add_constructor('!env', env_constructor)

    return loader

def required_get(data: dict, field: str):
    try: 
        return data[field]
    except KeyError as e:
        raise Exception(f'no required key {field} found') from e

class BaseConfig:
    
    @staticmethod
    def from_yaml(filename: str) -> 'BaseConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())
        
        return BaseConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> 'BaseConfig':
        res = BaseConfig()
        res.logger = logger.Config.from_dict(data.get('logger', {}))

        return res
