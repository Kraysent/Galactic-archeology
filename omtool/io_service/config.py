"""
Configuration objects of the io_service.
"""
from typing import List


def required_get(data: dict, field: str):
    """
    Tries to obtain the field from the dictionary and throws the
    error in case it was not found.
    """
    try:
        return data[field]
    except KeyError as ex:
        raise Exception(f"No required key {field} found in input configuration.") from ex


class Config:
    """
    Configuration for the io_service
    """

    format: str
    filenames: List[str]

    @staticmethod
    def from_dict(data: dict) -> "Config":
        """
        Loads this object from dictionary.
        """
        res = Config()
        res.format = data.get("format", "fits")
        res.filenames = required_get(data, "filenames")

        return res
