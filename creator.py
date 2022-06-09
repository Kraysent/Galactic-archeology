"""
Creation module for OMTool. Used to create and load models from
files and export them into single file.
"""
from pathlib import Path
from typing import Callable

from omtool import json_logger as logger
from omtool.core.creation import (
    CreationConfig,
    Object,
    SnapshotBuilder,
    SnapshotCreator,
    Type,
)
from omtool.core.datamodel import Snapshot, profiler


def create(config: CreationConfig):
    """
    Creation mode for the OMTool. Used to create and load models from
    files and export them into single file.
    """
    builder = SnapshotBuilder()

    if not config.overwrite:
        if Path(config.output_file).is_file():
            raise Exception(
                f'Output file ({config.output_file}) exists and "overwrite" '
                "option in creation config file is false (default)"
            )

    @profiler("Creation")
    def loop_creation_stage(body: Object):
        type_map: dict[Type, Callable[..., Snapshot]] = {
            Type.CSV: SnapshotCreator.construct_from_csv,
            Type.BODY: SnapshotCreator.construct_single_particle,
            Type.PLUMMER_SPHERE: SnapshotCreator.construct_plummer_sphere,
        }

        curr_snapshot = type_map[body.type](**body.args)

        curr_snapshot.particles.position += body.position
        curr_snapshot.particles.velocity += body.velocity

        logger.info(f"Adding snapshot of {len(curr_snapshot.particles)} particles.")
        builder.add_snapshot(curr_snapshot)
        logger.info("Snapshot added.")

    for body in config.objects:
        loop_creation_stage(body)

    builder.to_fits(config.output_file)
