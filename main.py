"""
Entry point of the program.
"""
import argparse
import atexit
import sys

import yaml

from analysis import analize
from creator import create
from integration import integrate
from omtool import json_logger as logger
from omtool.core.configs import (
    AnalysisConfigSchema,
    CreationConfigSchema,
    IntegrationConfigSchema,
)
from omtool.core.datamodel import task_profiler
from omtool.core.utils.config_utils import yaml_loader


def main():
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

    with open(args.inputparams[0], "r", encoding="utf-8") as stream:
        data = yaml.load(stream, Loader=yaml_loader())

    if args.mode == "create":
        create(CreationConfigSchema().load(data))
    elif args.mode == "integrate":
        integrate(IntegrationConfigSchema().load(data))
    elif args.mode == "analize":
        analize(AnalysisConfigSchema().load(data))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
