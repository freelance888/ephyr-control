import dataclasses
import json
from functools import partial

import gql
import yarl

__all__ = ("dtcls_to_json", "pretty_dtcls_to_json")


class EnhancedJSONEncoder(json.JSONEncoder):
    """JSON encoder.

    Extended to process specific object types as well.
    Credit: https://stackoverflow.com/a/51286749/6233648
    """

    def default(self, o):  # noqa: WPS111
        from ephyr_control.instance.constants import EphyrApiPaths

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, yarl.URL):
            return {"yarl.URL": f"yarl.URL('{o}')"}
        elif isinstance(o, gql.Client):
            return {"gql.Client": None}
        elif isinstance(o, EphyrApiPaths):
            return o.value
        return super().default(o)


dtcls_to_json = partial(json.dumps, cls=EnhancedJSONEncoder)

# pretty JSON https://docs.python.org/3/library/json.html
pretty_dtcls_to_json = partial(
    json.dumps,
    cls=EnhancedJSONEncoder,
    sort_keys=True,
    indent=2,
)
