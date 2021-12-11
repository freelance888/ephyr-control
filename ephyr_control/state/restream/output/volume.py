import dataclasses

__all__ = ('Volume',)


@dataclasses.dataclass
class Volume:
    level: int = 100  # percentage
    muted: bool = False
