#!/usr/bin/env python

import atexit
import sys
from typing import Callable

import click
import yaml
from zlog import logger

import omtool
from cli.config_utils import yaml_loader
from cli.python_schemas import (
    AnalysisConfigSchema,
    CreationConfigSchema,
    IntegrationConfigSchema,
)
from omtool.core.datamodel import task_profiler

close_funcs: list[Callable[[], None]] = []


@click.group()
def cli():
    pass


@cli.command(short_help="Generates JSON schema")
@click.option(
    "-c",
    "--creation",
    "creation_path",
    type=str,
    default="cli/schemas/creation_schema.json",
    show_default=True,
    help="Path where to save the creation schema to",
)
@click.option(
    "-i",
    "--integration",
    "integration_path",
    type=str,
    default="cli/schemas/integration_schema.json",
    show_default=True,
    help="Path where to save the integration schema to",
)
@click.option(
    "-a",
    "--analysis",
    "analysis_path",
    type=str,
    default="cli/schemas/analysis_schema.json",
    show_default=True,
    help="Path where to save the analysis schema to",
)
def generate_schema(creation_path, integration_path, analysis_path):
    """
    Generates JSON schema for all of the configuration files.
    """
    CreationConfigSchema().dump_schema(creation_path, indent=2, sort_keys=True)
    IntegrationConfigSchema().dump_schema(integration_path, indent=2, sort_keys=True)
    AnalysisConfigSchema().dump_schema(analysis_path, indent=2, sort_keys=True)


@cli.command(short_help="Exports snapshot into CSV")
@click.option(
    "-i", "--input-file", type=str, required=True, help="Path to input FITS file with snapshots."
)
@click.option("-o", "--output-file", type=str, required=True, help="Path to output FITS file.")
@click.option("-n", "--index", type=int, required=True, help="Index of snapshot inside input file.")
def csv_export(input_file, output_file, index):
    """
    Export particular snapshot from FITS into CSV file.
    """
    omtool.export_csv(input_file, output_file, index)


@cli.command(short_help="Create snapshot from config")
@click.argument("config")
def create(config):
    """
    A way to convert YAML description of the system into the snapshot with actual particles.

    CONFIG is a path to creation configuration file.
    """
    with open(config, "r", encoding="utf-8") as stream:
        data = yaml.load(stream, Loader=yaml_loader())

    omtool.create(CreationConfigSchema().load(data))


@cli.command(short_help="Evolve snapshot in time")
@click.argument("config")
def integrate(config):
    """
    A way to evolve system over given period of time.

    CONFIG is a path to integration configuration file.
    """
    with open(config, "r", encoding="utf-8") as stream:
        data = yaml.load(stream, Loader=yaml_loader())

    omtool.integrate(IntegrationConfigSchema().load(data), close_funcs)


@cli.command(short_help="Analize series of snapshots")
@click.argument("config")
def analize(config):
    """
    A way to analize system after the evolution.

    CONFIG is a path to analysis configuration file.
    """
    with open(config, "r", encoding="utf-8") as stream:
        data = yaml.load(stream, Loader=yaml_loader())

    omtool.analize(AnalysisConfigSchema().load(data), close_funcs)


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


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        for func in close_funcs:
            func()
