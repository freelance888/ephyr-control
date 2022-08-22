import enum

__all__ = ("EphyrApiPaths", "ALL_API_PATHS")


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


ALL_API_PATHS = tuple(EphyrApiPaths)
