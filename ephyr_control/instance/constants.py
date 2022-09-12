import enum

__all__ = (
    "MIXIN_UI_PATH",
    "EphyrPasswordKind",
    "EphyrApiPaths",
    "ALL_API_PATHS",
)


MIXIN_UI_PATH: str = "/mix"
""" Path to web UI used for concrete Output Mixin. """


class EphyrPasswordKind(enum.Enum):
    """Collection of password kinds (types).

    MAIN - for main UI (with restreams)
    OUTPUT - for pages regarding concrete output's UI
    """

    MAIN = "MAIN"
    OUTPUT = "OUTPUT"


class EphyrApiPaths(enum.Enum):
    """Collection of Ephyr API paths.
    Should start with '/'.

    /api - main API
    /api-mix - API for output mixin
    /api-dashboard - API for dashboard mode
    """

    API = "/api"
    MIXIN = "/api-mix"
    DASHBOARD = "/api-dashboard"


ALL_API_PATHS: tuple[EphyrApiPaths, ...] = tuple(EphyrApiPaths)
