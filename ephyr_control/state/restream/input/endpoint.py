import dataclasses
from typing import Optional

from ephyr_control.state import status

__all__ = ("Endpoint",)


@dataclasses.dataclass
class Endpoint:
    kind: str
    label: Optional[str] = dataclasses.field(default=None)
    status: str = dataclasses.field(default=status.OFFLINE)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["kind"],
            label=d.get("label"),
            status=d.get("status", status.OFFLINE),
        )


def rtmp_endpoint_factory(label: str = None):
    return Endpoint(kind="rtmp", label=label)
