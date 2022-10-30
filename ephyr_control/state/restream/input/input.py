import dataclasses
from typing import List, cast

from ephyr_control.custom_typing import UUID4

from ._mixins import _Input
from .endpoint import Endpoint, rtmp_endpoint_factory
from .failover_input import FailoverInput
from .input_source import InputSource

__all__ = ("NoFailoverInput", "Input", "UuidInput")


class NoFailoverInput(Exception):
    pass


@dataclasses.dataclass
class Input(_Input):
    KEY_DEFAULT = "origin"

    key: str = KEY_DEFAULT
    src: InputSource or None = dataclasses.field(default_factory=lambda: InputSource())

    def get_failover_input(self, idx: int) -> FailoverInput:
        if not self.src:
            raise NoFailoverInput("This Input does not have failover inputs.")
        try:
            return self.src.failover_inputs[idx]
        except IndexError as exc:
            raise NoFailoverInput(
                f"This Input does not have failover {idx}th input."
            ) from exc

    @property
    def primary_input(self) -> FailoverInput:
        return self.get_failover_input(0)

    @property
    def backup_input(self) -> FailoverInput:
        return self.get_failover_input(1)

    @classmethod
    def with_random_key(
        cls,
        key_prefix: str,
        key_random_chars: int = None,
        endpoints: List[Endpoint] = None,
        enabled: bool = True,
        src: InputSource or None = None,
    ) -> "Input":
        return cast(
            Input,
            super().with_random_key(
                key_prefix=key_prefix,
                key_random_chars=key_random_chars,
                endpoints=endpoints or [rtmp_endpoint_factory()],
                enabled=enabled,
                src=src or InputSource(),
            ),
        )

    @classmethod
    def with_random_keys(
        cls,
        key_prefix: str = KEY_DEFAULT,
        input_key_prefixes: [str, str] or None = InputSource.FI_KEYS_DEFAULT,
        key_random_chars: int = FailoverInput.KEY_RANDOM_LENGTH_DEFAULT,
    ) -> "Input":
        if input_key_prefixes is None:
            src = None
        else:
            src = InputSource.with_random_keys(
                key_prefixes=input_key_prefixes,
                key_random_chars=key_random_chars,
            )
        return cast(
            Input,
            cls.with_random_key(
                key_prefix=key_prefix,
                key_random_chars=key_random_chars,
                src=src,
            ),
        )


@dataclasses.dataclass
class UuidInput(Input):
    # id field is read-only
    id: UUID4 = None
