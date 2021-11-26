import yaml


class Config:
    def __init__(self, mapper: dict = None, defaults: dict = None) -> None:
        self.mapper = mapper

        if defaults is not None:
            for (key, value) in defaults.items():
                setattr(self, key, value)

    def get_unit(self, key, value):
        if self.mapper is None:
            return value

        if key in self.mapper: 
            return value | self.mapper[key]
        else: 
            return value

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
    def read_yaml(filename: str, mapper: dict = None) -> 'Config':
        data = {}
        res = Config(mapper = mapper)

        with open(filename, 'r') as stream:
            data = yaml.safe_load(stream)

        for (key, value) in data.items():
            setattr(res, key, res.get_unit(key, value))

        return res

    def write_yaml(self, filename: str):
        with open(filename, 'w') as stream:
            yaml.dump(self.to_dict(), stream)
