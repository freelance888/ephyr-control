import dataclasses

__all__ = ("Volume",)


@dataclasses.dataclass
class Volume:
    level: int = 100  # percentage
    muted: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Volume":
        return cls(d["level"], d["muted"])
