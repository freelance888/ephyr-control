"""Ephyr-control library.

Set of tools for managing Ephyr instances.
"""

__version__ = "1.0.0"

# import instance package only after state is ready
from .instance import EphyrInstance, RemoteEphyrInstance, Subscription
from .state import *
