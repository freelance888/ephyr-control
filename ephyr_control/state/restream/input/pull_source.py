import dataclasses

__all__ = ("PullSource",)


@dataclasses.dataclass
class PullSource:
    remote_url: str
