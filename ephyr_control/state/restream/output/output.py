import dataclasses
import uuid

from .volume import Volume

__all__ = ('Output', 'UuidOutput')


@dataclasses.dataclass
class Output:
    dst: str
    label: str = None
    enabled: bool = False
    preview_url: str = None
    volume: Volume = dataclasses.field(default_factory=Volume)


@dataclasses.dataclass
class UuidOutput(Output):
    # id field is read-only
    id: uuid.uuid4 = None
