import dataclasses
from typing import cast

from ephyr_control.custom_typing import UUID4
from ephyr_control.state.restream.input.pull_source import PullSource

from ._mixins import _Input

__all__ = (
    "FailoverInput",
    "UuidFailoverInput",
    "primary_input_factory",
    "backup1_input_factory",
    "backup2_input_factory",
)


@dataclasses.dataclass
class FailoverInput(_Input):
    src: PullSource = None

    KEY_PRIMARY = "primary"
    KEY_BACKUP1 = "backup1"
    KEY_BACKUP2 = "backup2"


def primary_input_factory(key_random_chars: int = 0) -> FailoverInput:
    return cast(
        FailoverInput,
        FailoverInput.with_random_key(
            key_prefix=FailoverInput.KEY_PRIMARY,
            key_random_chars=key_random_chars,
        ),
    )


def backup1_input_factory(key_random_chars: int = 0) -> FailoverInput:
    return cast(
        FailoverInput,
        FailoverInput.with_random_key(
            key_prefix=FailoverInput.KEY_BACKUP1,
            key_random_chars=key_random_chars,
        ),
    )


def backup2_input_factory(key_random_chars: int = 0) -> FailoverInput:
    return cast(
        FailoverInput,
        FailoverInput.with_random_key(
            key_prefix=FailoverInput.KEY_BACKUP2,
            key_random_chars=key_random_chars,
        ),
    )


@dataclasses.dataclass
class UuidFailoverInput(FailoverInput):
    # id field is read-only
    id: UUID4 = None
