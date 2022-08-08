from omtool.core.datamodel import AbstractModel, Snapshot
from omtool.core.models import register_model
from omtool.io_service import from_fits


@register_model(name="fits")
class FITSModel(AbstractModel):
    def __init__(self, filename: str, snapshot_number: int = 0):
        self.filename = filename
        self.snapshot_number = snapshot_number

    def run(self) -> Snapshot:
        it = from_fits(self.filename)

        i = 0
        for (i, snapshot_tuple) in enumerate(it):
            if i == self.snapshot_number:
                return Snapshot(*snapshot_tuple)

        raise ValueError("Model not found")
