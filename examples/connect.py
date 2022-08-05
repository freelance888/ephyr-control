"""
Example

Connect to Ephyr server and retrieve basic info.
"""

import json

from ephyr_control import RemoteEphyrInstance


inst = RemoteEphyrInstance(
    ipv4="13.14.15.16",  # use public IP address of your Ephyr server
)

# This method retrieves basic info about server
info = inst.get_info()

# prettify and print
print(json.dumps(info, indent=2))
