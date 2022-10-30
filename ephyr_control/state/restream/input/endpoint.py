import dataclasses

__all__ = ("Endpoint",)


@dataclasses.dataclass
class Endpoint:
    kind: str


def rtmp_endpoint_factory():
    return Endpoint(kind="rtmp")
