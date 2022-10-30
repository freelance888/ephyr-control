import dataclasses
import uuid
from typing import ClassVar, List

from ephyr_control.utils import build_rtmp_uri, generate_random_key_of_length

from ..constant import RESTREAM_KEY_MAXLENGTH
from ._mixins import _KeyedMixin
from .input import FailoverInput, Input
from .output import Output

__all__ = ("Restream", "UuidRestream", "HostAwareRestream")


@dataclasses.dataclass
class Restream(_KeyedMixin):
    key: str = dataclasses.field(
        default_factory=lambda: generate_random_key_of_length(length=4)
    )
    label: str = None
    outputs: List[Output] = dataclasses.field(default_factory=list)
    input: Input = dataclasses.field(default_factory=Input)

    # Ephyr restrictions
    KEY_MAXLENGTH: ClassVar[int] = RESTREAM_KEY_MAXLENGTH

    @property
    def main_input(self) -> FailoverInput:
        return self.input.main_input

    @property
    def backup_input(self) -> FailoverInput:
        return self.input.backup_input

    @property
    def path(self) -> str:
        return self.key

    def pull_from_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.input.key,
        )

    def push_to_uris(self, host: str) -> [str, ...]:
        if self.input.src is None:
            return [self.pull_from_uri(host=host)]
        else:
            return [
                build_rtmp_uri(
                    host=host,
                    path=self.path,
                    key=failover_input.key,
                )
                for failover_input in self.input.src.failover_inputs
            ]

    def push_to_main_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.main_input.key,
        )

    def push_to_backup_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.backup_input.key,
        )


@dataclasses.dataclass
class UuidRestream(Restream):
    # id field is read-only
    id: uuid.uuid4 = None


@dataclasses.dataclass
class HostAwareRestream(Restream):
    """This class remembers it's host for easier URI generation,
    but don't turn it in JSON and paste to Ephyr - convert it back
    to normal Restream first with .make_unaware method."""

    host: str = None  # well, actually, its required.

    def pull_from_uri(self) -> str:
        return super().pull_from_uri(host=self.host)

    def push_to_uris(self) -> [str, ...]:
        return super().push_to_uris(host=self.host)

    def push_to_main_uri(self) -> str:
        return super().push_to_main_uri(host=self.host)

    def push_to_backup_uri(self) -> str:
        return super().push_to_backup_uri(host=self.host)
