from typing import List, Optional

from .custom_typing import TypedDict


class EphyrConfig(TypedDict):
    ipv4: str  # unique across all configs
    domain: Optional[str]
    title: Optional[str]  # unique across all configs
    password: Optional[str]


class EphyrConfigFull(EphyrConfig):
    restreams: List[dict]
