"""
Logger service that provides functionality to print logs
into JSON into different destinations.
"""
from omtool.json_logger.config import Config, LoggerConfigSchema
from omtool.json_logger.main import debug, error, info, initialize, warning
