import dataclasses

from ephyr_control.state import status

__all__ = ("Endpoint",)


@dataclasses.dataclass
class Endpoint:
    kind: str
    status: str = dataclasses.field(default=status.OFFLINE)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["kind"],
            status=d.get("status", status.OFFLINE),
        )


def rtmp_endpoint_factory():
    return Endpoint(kind="rtmp")
