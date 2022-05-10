'''
Configuration objects' description of the creation module.
'''
from enum import Enum
from typing import List

import yaml
from amuse.lab import units, VectorQuantity, ScalarQuantity
from omtool.core.utils import yaml_loader, required_get


class Type(Enum):
    '''
    Lists types of the object that dould be added.
    '''
    BODY = 1
    CSV = 2

    @staticmethod
    def from_string(string: str) -> 'Type':
        '''
        Converts string representation of the type into this enum.
        '''
        if string.lower() == 'body':
            return Type.BODY
        elif string.lower() == 'csv':
            return Type.CSV
        else:
            raise Exception(f'Unknown object type "{string}"')

class Object:
    '''
    Body or CSV file configuration.
    '''
    delimeter: str
    position: VectorQuantity
    velocity: VectorQuantity
    type: Type
    path: str
    mass: ScalarQuantity

    @staticmethod
    def from_dict(data: dict) -> 'Object':
        '''
        Loads this type from dictionary.
        '''
        res = Object()
        res.delimeter = data.get('delimeter', ',')
        res.position = data.get('position', [0, 0, 0] | units.kpc)
        res.velocity = data.get('velocity', [0, 0, 0] | units.kms)
        res.type = Type.from_string(required_get(data, 'type'))

        if res.type == Type.CSV:
            res.path = required_get(data, 'path')
        elif res.type == Type.BODY:
            res.mass = required_get(data, 'mass')

        return res

class CreationConfig:
    '''
    The highes level of creation configuration
    '''
    output_file: str
    objects: List[Object]
    overwrite: bool

    @staticmethod
    def from_yaml(filename: str) -> 'CreationConfig':
        '''
        Loads this type from the actual YAML file.
        '''
        data = {}

        with open(filename, 'r', encoding = 'utf-8') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        return CreationConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> 'CreationConfig':
        '''
        Loads this type from dictionary.
        '''
        res = CreationConfig()
        res.output_file = required_get(data, 'output_file')
        res.objects = [
            Object.from_dict(object) for object in required_get(data, 'objects')
        ]
        res.overwrite = data.get('overwrite', False)

        return res
