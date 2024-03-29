import dataclasses
from typing import ClassVar, List, cast

from ...constant import INPUT_KEY_MAXLENGTH
from .._mixins import _KeyedMixin
from .endpoint import Endpoint, rtmp_endpoint_factory

__all__ = ("_Input",)


@dataclasses.dataclass
class _Input(_KeyedMixin):
    endpoints: List[Endpoint] = dataclasses.field(
        default_factory=lambda: [rtmp_endpoint_factory()],
    )
    enabled: bool = True

    # Ephyr restrictions
    KEY_MAXLENGTH: ClassVar[int] = INPUT_KEY_MAXLENGTH

    @classmethod
    def with_random_key(  # noqa: WPS211
        cls,
        key_prefix: str,
        key_random_chars: int = None,
        endpoints: List[Endpoint] = None,
        enabled: bool = True,
        **kwargs,
    ) -> "_Input":
        return cast(
            _Input,
            super().with_random_key(
                key_prefix=key_prefix,
                key_random_chars=key_random_chars,
                endpoints=endpoints or [rtmp_endpoint_factory()],
                enabled=enabled,
                **kwargs,
            ),
        )
