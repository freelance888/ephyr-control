import sys
import uuid

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict, overload  # noqa
else:
    from typing_extensions import Literal, TypedDict, overload  # noqa


UUID4 = uuid.UUID  # uuid.uuid4
