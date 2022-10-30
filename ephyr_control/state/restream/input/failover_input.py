import dataclasses
from typing import cast

from ephyr_control.custom_typing import UUID4
from ephyr_control.state.restream.input.pull_source import PullSource

from ._mixins import _Input

__all__ = (
    "FailoverInput",
    "UuidFailoverInput",
)


@dataclasses.dataclass
class FailoverInput(_Input):
    src: PullSource = None

    KEY_MAIN = "main"
    KEY_BACKUP = "backup"


def main_input_factory(key_random_chars: int = 0) -> FailoverInput:
    return cast(
        FailoverInput,
        FailoverInput.with_random_key(
            key_prefix=FailoverInput.KEY_MAIN,
            key_random_chars=key_random_chars,
        ),
    )


def backup_input_factory(key_random_chars: int = 0) -> FailoverInput:
    return cast(
        FailoverInput,
        FailoverInput.with_random_key(
            key_prefix=FailoverInput.KEY_BACKUP,
            key_random_chars=key_random_chars,
        ),
    )


@dataclasses.dataclass
class UuidFailoverInput(FailoverInput):
    # id field is read-only
    id: UUID4 = None
