import sys
import typing
import uuid

if sys.version_info >= (3, 8):
    from typing import (  # noqa
        Literal,
        TypedDict,
        overload,
    )
else:
    from typing_extensions import (  # noqa
        Literal,
        TypedDict,
        NotRequired,
        Required,
        overload,
    )

from typing_extensions import (  # noqa
    NotRequired,
    Required,
)

UUID4 = uuid.UUID  # uuid.uuid4
IPv4 = typing.NewType("IPv4", str)
