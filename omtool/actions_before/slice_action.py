import math

from amuse.lab import Particles
from zlog import logger

from omtool.core.datamodel import Snapshot


def slice_action(
    snapshot: Snapshot,
    parts: list[tuple[float, float]] | None = None,
    part: list[int] | None = None,
    ids: list[int] | None = None,
    id: int | None = None,
) -> Snapshot:
    slices: list[tuple[int, int]] = []

    if parts is not None:
        length = len(snapshot.particles)

        for start, end in parts:
            if not 0 <= start <= 1 or not 0 <= end <= 1:
                raise ValueError(
                    "start and end of the slice action values must be inside the [0, 1] interval"
                )

            slices.append((math.floor(start * length), math.floor(end * length)))

    if part is not None:
        if len(part) != 2:
            raise ValueError("part argument should have exactly two elements")

        slices.append((part[0], part[1]))

    ids = ids or []

    if id is not None:
        ids.append(id)

    for id in ids:
        if id >= len(snapshot.particles) or id < 0:
            logger.warn().int("id", id).msg("particle id outside of boundaries")

        slices.append((id, id + 1))

    result = Snapshot(Particles(), snapshot.timestamp)

    for start, end in slices:
        result.particles.add_particles(snapshot.particles[start:end])

    return result
