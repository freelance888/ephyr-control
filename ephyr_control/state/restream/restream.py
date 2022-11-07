import dataclasses
from typing import ClassVar, List

from ephyr_control.custom_typing import UUID4
from ephyr_control.utils import build_rtmp_uri, generate_random_key_of_length

from ..constant import RESTREAM_KEY_MAXLENGTH
from ._mixins import _KeyedMixin
from .input import FailoverInput, Input
from .output import Output, UuidOutput, make_output

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

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d["key"],
            d.get("label"),
            outputs=[make_output(otp) for otp in d["outputs"]],
            input=Input.from_dict(d["input"]),
        )

    @property
    def primary_input(self) -> FailoverInput:
        return self.input.primary_input

    @property
    def backup1_input(self) -> FailoverInput:
        return self.input.backup1_input

    @property
    def backup2_input(self) -> FailoverInput:
        return self.input.backup2_input

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

    def push_to_primary_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.primary_input.key,
        )

    def push_to_backup1_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.backup1_input.key,
        )

    def push_to_backup2_uri(self, host: str) -> str:
        return build_rtmp_uri(
            host=host,
            path=self.path,
            key=self.backup2_input.key,
        )


@dataclasses.dataclass
class UuidRestream(Restream):
    outputs: List[UuidOutput] = dataclasses.field(default_factory=list)

    # id field is read-only
    id: UUID4 = None

    @classmethod
    def from_dict(cls, d: dict):
        restream = Restream.from_dict(d)
        restream.id = UUID4(d["id"])
        return restream


@dataclasses.dataclass
class HostAwareRestream(Restream):
    """This class remembers its host for easier URI generation,
    but don't turn it in JSON and paste to Ephyr - convert it back
    to normal Restream first with .make_unaware method."""

    host: str = None  # well, actually, its required.

    def pull_from_uri(self) -> str:
        return super().pull_from_uri(host=self.host)

    def push_to_uris(self) -> [str, ...]:
        return super().push_to_uris(host=self.host)

    def push_to_primary_uri(self) -> str:
        return super().push_to_primary_uri(host=self.host)

    def push_to_backup1_uri(self) -> str:
        return super().push_to_backup1_uri(host=self.host)

    def push_to_backup2_uri(self) -> str:
        return super().push_to_backup2_uri(host=self.host)
