from omtool.core import datamodel
from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="fits")
class FITSModel(AbstractModel):
    def __init__(self, filename: str, snapshot_number: int = 0):
        self.filename = filename
        self.snapshot_number = snapshot_number

    def run(self) -> Snapshot:
        it = datamodel.from_fits(self.filename)

        i = 0
        for (i, snapshot) in enumerate(it):
            if i == self.snapshot_number:
                return snapshot

        raise ValueError("Model not found")
