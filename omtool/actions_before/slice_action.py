from typing import Optional

from omtool.core.datamodel import Snapshot


def slice_action(snapshot: Snapshot, part: Optional[list[int]] = None, id: int = 0) -> Snapshot:
    if part is None:
        part = [id, id + 1]

    return snapshot[slice(*part)]
