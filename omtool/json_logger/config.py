"""
General config for logger.
"""


class Config:
    """
    General config for logger.
    """

    filename: str
    datefmt: str

    @staticmethod
    def from_dict(data: dict):
        """
        Loads this type from dict.
        """
        res = Config()
        res.filename = data.get("filename", "")
        res.datefmt = data.get("datefmt", "%Y-%m-%d %H:%M:%S")

        return res
