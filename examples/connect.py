"""
Example

Connect to Ephyr server and retrieve basic info.
"""

import json

from ephyr_control import RemoteEphyrInstance

IPv4 = "13.14.15.16"  # use public IP address of your Ephyr server
PASSWORD = None  # leave None to access password-less instance


inst = RemoteEphyrInstance(
    ipv4=IPv4,  # the only required argument
    password=PASSWORD,  # optional argument, can be omitted
    https=False,  # optional argument, modifies port
    title="that instance",  # optional argument, for humans
    domain="mydomain.online",  # optional argument, handful for readable links
)

# This method retrieves basic info about server
info = inst.get_info()

# prettify and print
print(json.dumps(info, indent=2))

# change password, and verify that instance is still usable
inst.change_password("new_fAnCy+P@55w0rd")
print(json.dumps(inst.get_info(), indent=2))
