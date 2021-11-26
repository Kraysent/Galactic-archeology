from amuse.lab import units
from amuse.units.core import named_unit
import yaml

unit_names = ['Myr', 'kpc', 'kms']
units = [units.Myr, units.kpc, units.kms]

def str_to_unit(s: str) -> named_unit:
    index = unit_names.index(s) if s in unit_names else None

    if index is not None:
        return units[index]
    else:
        raise RuntimeError(f'{str} is unsupported unit name.')

def unit_to_str(u: named_unit) -> str:
    index = units.index(u) if u in units else None

    if index is not None:
        return unit_names[index]
    else:
        raise RuntimeError(f'{u} is unsupported unit.')

class Config:
    def __init__(self, mapper: dict = None, defaults: dict = None) -> None:
        self.mapper = mapper

        if defaults is not None:
            for (key, value) in defaults.items():
                setattr(self, key, value)

    def to_dict(self):
        tmp = self.__dict__
        data = {}

        for (key, value) in tmp.items():
            if key == 'mapper': continue
            if value != self.get_unit(key, value):
                data[key] = value.value_in(self.get_unit(key, value))
            else: 
                data[key] = value

        return data

    @staticmethod
    def from_yaml(filename: str) -> 'Config':
        data = {}
        res = Config()

        with open(filename, 'r') as stream:
            data = yaml.safe_load(stream)

        for (key, value) in data.items():
            if isinstance(value, str):
                value = value.split(' ')

                if len(value) == 1:
                    setattr(res, key, value[0])
                else:
                    setattr(res, key, float(value[0]) | str_to_unit(value[1]))
            else:
                setattr(res, key, value)

        return res
