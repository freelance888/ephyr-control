__version__ = "1.0.0"

# import instance package only after state is ready
from .instance import EphyrInstance, RemoteEphyrInstance
from .state import *
