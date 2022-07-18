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
        choices=["create", "integrate", "analize", "generate-schema"],
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

    match args.mode:
        case "create":
            with open(args.inputparams[0], "r", encoding="utf-8") as stream:
                data = yaml.load(stream, Loader=yaml_loader())

            create(CreationConfigSchema().load(data))
        case "integrate":
            with open(args.inputparams[0], "r", encoding="utf-8") as stream:
                data = yaml.load(stream, Loader=yaml_loader())

            integrate(IntegrationConfigSchema().load(data))
        case "analize":
            with open(args.inputparams[0], "r", encoding="utf-8") as stream:
                data = yaml.load(stream, Loader=yaml_loader())

            analize(AnalysisConfigSchema().load(data))
        case "generate-schema":
            CreationConfigSchema().dump_schema("schemas/creation_schema.json", indent=2)
            IntegrationConfigSchema().dump_schema("schemas/integration_schema.json", indent=2)
            AnalysisConfigSchema().dump_schema("schemas/analysis_schema.json", indent=2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
