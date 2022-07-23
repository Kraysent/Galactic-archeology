import sys

from zlog import ConsoleFormatter, FormattedStream, JSONFormatter, Level, logger


def initialize_logger(filename: str = "", **kwargs):
    logger.base_level = Level.INFO
    logger.formatted_streams = [
        FormattedStream(ConsoleFormatter(), sys.stdout),
    ]

    if filename != "":
        # TODO: should probably close this file somewhere
        logger.formatted_streams.append(FormattedStream(JSONFormatter(), open(filename, "a", 1)))
