import dataclasses
import uuid
from typing import List

from .volume import Volume
from .output import Output, UuidOutput

__all__ = ("Mixin", "OutputWithMixins", "UuidOutputWithMixins")


@dataclasses.dataclass
class Mixin:
    """
    Note: this class is no a "mixin" by the standard meaning of this word in Python OOP.
    It only referes to an entity in Ephyr state structure that mixes video and audio.
    """

    src: str
    volume: Volume = None
    delay: str = "3s 500ms"

    @classmethod
    def from_dict(cls, d: dict) -> "Mixin":
        if "volume" in d:
            volume = Volume(**d.pop("volume"))
        else:
            volume = None
        return cls(**d, volume=volume)


@dataclasses.dataclass
class OutputWithMixins(Output):
    mixins: List[Mixin] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class UuidOutputWithMixins(OutputWithMixins, UuidOutput):
    # id field is read-only
    id: uuid.uuid4 = None
