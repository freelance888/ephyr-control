import dataclasses
from typing import List

from .failover_input import (
    FailoverInput,
    main_input_factory,
    backup_input_factory,
)

__all__ = ("InputSource",)


@dataclasses.dataclass
class InputSource:
    failover_inputs: List[FailoverInput] = dataclasses.field(
        default_factory=lambda: [main_input_factory(), backup_input_factory()]
    )

    FI_KEYS_DEFAULT = (FailoverInput.KEY_MAIN, FailoverInput.KEY_BACKUP)

    def __post_init__(self):
        # ensure unique restream keys
        if len({foi.key for foi in self.failover_inputs}) < len(
            self.failover_inputs
        ):
            raise ValueError("Not all FailoverInput keys are unique.")

    def get_foinput_by_key(self, foinput_key: str):
        try:
            return next(
                filter(lambda foi: foi.key == foinput_key, self.failover_inputs)
            )
        except StopIteration:
            raise KeyError(f'FailoverInput with key="{foinput_key}" not found.')

    @property
    def main_input(self) -> FailoverInput:
        return self.failover_inputs[0]

    @property
    def backup_input(self) -> FailoverInput:
        return self.failover_inputs[1]

    @classmethod
    def with_random_keys(
        cls,
        key_prefixes: [str, str] = FI_KEYS_DEFAULT,
        key_random_chars: int = FailoverInput.KEY_RANDOM_LENGTH_DEFAULT,
    ) -> "InputSource":
        return cls(
            failover_inputs=[
                FailoverInput.with_random_key(
                    key_prefix=key_prefix,
                    key_random_chars=key_random_chars,
                )
                for key_prefix in key_prefixes
            ]
        )
