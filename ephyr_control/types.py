from typing import List

from .custom_typing import NotRequired, Required, TypedDict


class EphyrConfig(TypedDict):
    ipv4: Required[str]  # unique across all configs
    domain: NotRequired[str]
    title: NotRequired[str]  # unique across all configs
    password: NotRequired[str]


class EphyrConfigFull(EphyrConfig):
    restreams: Required[List[dict]]
