import enum

__all__ = ("EphyrApiPaths", "ALL_API_PATHS")


class EphyrApiPaths(enum.Enum):
    """Collection of Ephyr API paths.
    Should start with '/'.

    /api - main API
    /dashboard - API for dashboard mode
    """

    API = "/api"
    DASHBOARD = "/dashboard"


ALL_API_PATHS = tuple(EphyrApiPaths)
