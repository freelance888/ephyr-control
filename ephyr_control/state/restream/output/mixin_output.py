import dataclasses
from typing import List

from ephyr_control.custom_typing import UUID4

from .output import Output, UuidOutput
from .volume import Volume

__all__ = ("Mixin", "OutputWithMixins", "UuidOutputWithMixins")


@dataclasses.dataclass
class Mixin:
    """Mixin is Ephyr's name for entity that mixes audio and video.

    Note: this class is no a "mixin" by the standard meaning of this word
    in Python OOP.
    It only refers to an entity in Ephyr state structure that mixes
    video and audio.
    """

    src: str
    volume: Volume = None
    delay: str = "3s 500ms"
    sidechain: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Mixin":
        return cls(
            src=d["src"],
            volume=Volume.from_dict(d["volume"]),
            delay=d["delay"],
            sidechain=d["sidechain"],
        )


class UuidMixin(Mixin):
    # id field is read-only
    id: UUID4 = None

    @classmethod
    def from_dict(cls, d: dict) -> "Mixin":
        mixin = Mixin.from_dict(d)
        mixin.id = UUID4(d["id"])
        return mixin


@dataclasses.dataclass
class OutputWithMixins(Output):
    mixins: List[Mixin] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "OutputWithMixins":
        output = Output.from_dict(d)
        output.mixins = [Mixin.from_dict(m) for m in d["mixins"]]
        return output


@dataclasses.dataclass
class UuidOutputWithMixins(OutputWithMixins, UuidOutput):
    # id field is read-only
    id: UUID4 = None

    @classmethod
    def from_dict(cls, d: dict) -> "OutputWithMixins":
        output = Output.from_dict(d)
        output.mixins = [UuidMixin.from_dict(m) for m in d["mixins"]]
        output.id = UUID4(d["id"])
        return output
