from enum import Enum
from typing import List
from amuse.lab import units

import yaml
from amuse.lab import ScalarQuantity, VectorQuantity
from omtool.datamodel import yaml_loader


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
    type: Type
    mass: ScalarQuantity
    position: VectorQuantity
    velocity: VectorQuantity
    delimeter: str
    path: str

    @staticmethod
    def from_dict(input: dict) -> 'Object':
        res = Object()
        res.delimeter = ','
        res.position = [0, 0, 0] | units.kpc
        res.velocity = [0, 0, 0] | units.kms

        if 'type' in input:
            res.type = Type.from_string(input['type'])

            if res.type == Type.CSV:
                if 'path' in input:
                    res.path = input['path']
                else: 
                    raise Exception('No path to csv specified')
                
                if 'delimeter' in input:
                    res.delimeter = input['delimeter']
            elif res.type == Type.BODY:
                if 'mass' in input:
                    res.mass = input['mass']
                else:
                    raise Exception('No mass of the object specified')
            
        if 'position' in input:
            res.position = input['position']
        
        if 'velocity' in input:
            res.velocity = input['velocity']

        return res

class CreationConfig:
    output_file: str
    objects: List[Object]

    @staticmethod
    def from_yaml(filename: str) -> 'CreationConfig':
        data = {}

        with open(filename, 'r') as stream:
            data = yaml.load(stream, Loader = yaml_loader())

        res = CreationConfig()
        res.output_file = ''
        res.objects = []

        if 'output_file' in data:
            res.output_file = data['output_file']
        else:
            raise Exception("No output file specified in creation configuration file")
    
        if 'objects' in data:
            for object in data['objects']:
                res.objects.append(Object.from_dict(object))
        else:
            raise Exception("No objects specified in creation configuration file")

        return res