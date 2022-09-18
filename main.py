#!/usr/bin/env python

import argparse
import atexit
import sys

import yaml
from zlog import logger

from cli.config_utils import yaml_loader
from cli.python_schemas import (
    AnalysisConfigSchema,
    CreationConfigSchema,
    IntegrationConfigSchema,
)
from omtool import analize, create, integrate
from omtool.core.datamodel import task_profiler


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
            (
                logger.debug()
                .string("stage", key)
                .measured_float("t", val, "s", decimals=3)
                .msg("Average timing")
            )

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
            CreationConfigSchema().dump_schema(
                "cli/schemas/creation_schema.json", indent=2, sort_keys=True
            )
            IntegrationConfigSchema().dump_schema(
                "cli/schemas/integration_schema.json", indent=2, sort_keys=True
            )
            AnalysisConfigSchema().dump_schema(
                "cli/schemas/analysis_schema.json", indent=2, sort_keys=True
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
