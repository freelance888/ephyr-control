import sys
import typing
import uuid

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict, overload  # noqa
else:
    from typing_extensions import (  # noqa
        Literal,
        TypedDict,
        NotRequired,
        Required,
        overload,
    )

from typing_extensions import NotRequired, Required  # noqa

UUID4 = uuid.UUID  # uuid.uuid4
IPv4 = typing.NewType("IPv4", str)
