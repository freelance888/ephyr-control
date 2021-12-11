import dataclasses

from .constant import EPHYR_CONFIG_VERSION
from .restream import Restream
from .settings import Settings
from ..utils.serialization import dtcls_to_json, pretty_dtcls_to_json

__all__ = ("State",)


@dataclasses.dataclass
class State:
    restreams: [Restream, ...] = dataclasses.field(default_factory=list)
    settings: Settings = None
    version: str = EPHYR_CONFIG_VERSION

    def __post_init__(self):
        # ensure unique restream keys
        if len({r.key for r in self.restreams}) < len(self.restreams):
            raise ValueError("Not all restream keys are unique.")

    def get_restream_by_key(self, restream_key: str) -> Restream:
        try:
            return next(filter(lambda r: r.key == restream_key, self.restreams))
        except StopIteration:
            raise KeyError(f'Restream with key="{restream_key}" not found.')

    def to_json(self, cleanup: bool = True, prettify: bool = False) -> str:
        # FIXME: ignore cleanup
        if prettify:
            return pretty_dtcls_to_json(self)
        else:
            return dtcls_to_json(self)
