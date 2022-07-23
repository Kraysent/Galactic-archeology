"""
Creation module for OMTool. Used to create and load models from
files and export them into single file.
"""
from pathlib import Path
from typing import Callable, Dict

from amuse.lab import units
from zlog import logger

from omtool.core.configs import CreationConfig, Object, Type
from omtool.core.creation import SnapshotBuilder, SnapshotCreator
from omtool.core.datamodel import Snapshot, profiler
from omtool.core.utils import initialize_logger


def create(config: CreationConfig):
    """
    Creation mode for the OMTool. Used to create and load models from
    files and export them into single file.
    """
    initialize_logger(**config.logging)
    builder = SnapshotBuilder()

    if not config.overwrite:
        if Path(config.output_file).is_file():
            raise Exception(
                f'Output file ({config.output_file}) exists and "overwrite" '
                "option in creation config file is false (default)"
            )

    @profiler("Creation")
    def loop_creation_stage(body: Object):
        type_map: Dict[Type, Callable[..., Snapshot]] = {
            Type.csv: SnapshotCreator.construct_from_csv,
            Type.body: SnapshotCreator.construct_single_particle,
            Type.plummer_sphere: SnapshotCreator.construct_plummer_sphere,
        }

        curr_snapshot = type_map[body.type](**body.args)

        curr_snapshot.particles.position += body.position
        curr_snapshot.particles.velocity += body.velocity

        if body.downsample_to is not None:
            c = len(curr_snapshot.particles) / body.downsample_to
            curr_snapshot.particles = curr_snapshot.particles[:: int(c)]
            curr_snapshot.particles.mass *= c

        (
            logger.info()
            .int("n", len(curr_snapshot.particles))
            .measured_float(
                "total_mass", curr_snapshot.particles.total_mass().value_in(units.MSun), "MSun"
            )
            .msg("Add particles")
        )
        builder.add_snapshot(curr_snapshot)

    for body in config.objects:
        loop_creation_stage(body)

    builder.to_fits(config.output_file)
