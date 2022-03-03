from enum import Enum
from typing import List

import yaml
from amuse.lab import ScalarQuantity, VectorQuantity, units
from omtool.datamodel import yaml_loader
from omtool.datamodel.config import required_get


class Type(Enum):
    BODY = 1
    CSV = 2

    @staticmethod
    def from_string(string: str) -> 'Type':
        if string.lower() == 'body':
            return Type.BODY
        elif string.lower() == 'csv':
            return Type.CSV
        else:
            raise Exception(f'Unknown object type "{string}"')

class Object:
    @staticmethod
    def from_dict(input: dict) -> 'Object':
        res = Object()
        res.delimeter = input.get('delimeter', ',')
        res.position = input.get('position', [0, 0, 0] | units.kpc)
        res.velocity = input.get('velocity', [0, 0, 0] | units.kms)
        res.type = Type.from_string(required_get(input, 'type'))

        if res.type == Type.CSV:
            res.path = required_get(input, 'path')
        elif res.type == Type.BODY:
            res.mass = required_get(input, 'mass')

        return res

class CreationConfig:
    @staticmethod
    def from_yaml(filename: str) -> 'CreationConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        return CreationConfig.from_dict(data)

    @staticmethod
    def from_dict(input: dict) -> 'CreationConfig':
        res = CreationConfig()
        res.output_file = required_get(input, 'output_file')
        res.objects = [
            Object.from_dict(object) for object in required_get(input, 'objects')
        ]
        res.overwrite = input.get('overwrite', False)

        return res
