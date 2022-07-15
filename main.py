"""
Entry point of the program.
"""
import argparse
import atexit

import yaml

from analysis import analize
from creator import create
from integration import integrate
from omtool import json_logger as logger
from omtool.core.analysis import AnalysisConfig
from omtool.core.datamodel import BaseConfig, task_profiler
from omtool.core.datamodel import CreationConfigSchema
from omtool.core.integration import IntegrationConfig
from omtool.core.utils.config_utils import yaml_loader

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        help="Mode of the program to run",
        choices=["create", "integrate", "analize", "test"],
    )
    parser.add_argument(
        "inputparams",
        help="input parameters for particular mode (for example, path to config file)",
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args()

    @atexit.register
    def _print_times():
        res = task_profiler.dump_times()

        for key, val in res.items():
            logger.info(f"{key} worked {val:.02f} seconds on average")

    baseConfig = BaseConfig.from_yaml(args.inputparams[0])
    logger.initialize(baseConfig.logger)

    if args.mode == "create":
        with open(args.inputparams[0], "r", encoding="utf-8") as stream:
            data = yaml.load(stream, Loader=yaml_loader())

        schema = CreationConfigSchema()
        create(schema.load(data))
    elif args.mode == "integrate":
        integrate(IntegrationConfig.from_yaml(args.inputparams[0]))
    elif args.mode == "analize":
        analize(AnalysisConfig.from_yaml(args.inputparams[0]))
