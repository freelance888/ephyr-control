import dataclasses
from typing import ClassVar

from ephyr_control.state.constant import (
    INPUT_KEY_MAXLENGTH,
    RESTREAM_KEY_MAXLENGTH,
)
from ephyr_control.utils import generate_random_key_of_length


@dataclasses.dataclass
class _KeyedMixin:
    """
    Mixin for entities with "key" param.

    Note: this class is a Mixin in the standard meaning of "mixin"
    word in Python OOP.
    """

    key: str

    # Epyr restriction. must be overwritten by inheritor
    KEY_MAXLENGTH: ClassVar[int] = min(INPUT_KEY_MAXLENGTH, RESTREAM_KEY_MAXLENGTH)

    # Constants of this implementation
    KEY_SEP: ClassVar[str] = "_"
    KEY_RANDOM_LENGTH_DEFAULT: ClassVar[int] = 8

    def __post_init__(self):
        if len(self.key) > self.KEY_MAXLENGTH:
            raise ValueError(
                f"key is too long. Maximum is {self.KEY_MAXLENGTH}, "
                f"got {len(self.key)}: {self.key}"
            )

    @classmethod
    def build_key_with_random(cls, prefix: str, length: int = None) -> str:
        if length == 0:
            return prefix
        elif length < 0:
            raise ValueError("length must be positive")
        random_suffix = generate_random_key_of_length(
            length=length if length is not None else cls.KEY_RANDOM_LENGTH_DEFAULT,
        )
        return prefix + cls.KEY_SEP + random_suffix

    @classmethod
    def with_random_key(
        cls, key_prefix: str, key_random_chars: int = None, **kwargs
    ) -> "_KeyedMixin":
        return cls(
            key=cls.build_key_with_random(
                prefix=key_prefix,
                length=key_random_chars,
            ),
            **kwargs,
        )
