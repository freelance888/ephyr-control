import dataclasses

__all__ = ("Endpoint",)


@dataclasses.dataclass
class Endpoint:
    kind: str


rtmp_endpoint_factory = lambda: Endpoint(kind="rtmp")
