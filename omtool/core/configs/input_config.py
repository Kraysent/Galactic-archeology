from dataclasses import dataclass


@dataclass
class InputConfig:
    format: str
    filenames: list[str]
