from typing import List


def required_get(data: dict, field: str):
    try:
        return data[field]
    except KeyError as e:
        raise Exception(f'No required key {field} found in input configuration.') from e

class Config:
    format: str
    filenames: List[str]

    @staticmethod
    def from_dict(data: dict) -> 'Config':
        res = Config()
        res.format = data.get('format', 'fits')
        res.filenames = required_get(data, 'filenames')

        return res
