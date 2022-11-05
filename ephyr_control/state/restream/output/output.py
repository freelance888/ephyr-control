import dataclasses

from ephyr_control.custom_typing import UUID4

from .volume import Volume

__all__ = ("Output", "UuidOutput")


@dataclasses.dataclass
class Output:
    dst: str
    label: str = None
    enabled: bool = False
    preview_url: str = None
    volume: Volume = dataclasses.field(default_factory=Volume)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["dst"],
            d.get("label"),
            d["enabled"],
            d.get("preview_url"),
            Volume.from_dict(d["volume"]),
        )


@dataclasses.dataclass
class UuidOutput(Output):
    # id field is read-only
    id: UUID4 = None

    @classmethod
    def from_dict(cls, d: dict):
        output = Output.from_dict(d)
        output.id = UUID4(d["id"])
        return output
