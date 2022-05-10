"""
Common methods and base class for all the configurations.
"""
import yaml
from omtool import json_logger as logger
from omtool.core.utils import yaml_loader

class BaseConfig:
    """
    Preprocesses every config file to obtain the common configurations.
    """

    logger: logger.Config

    @staticmethod
    def from_yaml(filename: str) -> "BaseConfig":
        """
        Read this object from the actual YAML file.
        """
        data = {}

        with open(filename, "r", encoding="utf-8") as stream:
            data = yaml.load(stream, Loader=yaml_loader())

        return BaseConfig.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "BaseConfig":
        """
        Read this object from the dictionary.
        """
        res = BaseConfig()
        res.logger = logger.Config.from_dict(data.get("logging", {}))

        return res
