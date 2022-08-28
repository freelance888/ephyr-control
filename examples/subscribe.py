"""
Example of subscription.

This example demonstrates how to use subscription operations.
"""

import asyncio

from ephyr_control.instance.instance import EphyrInstance
from ephyr_control.instance.queries import api_subscribe_state
from ephyr_control.instance.subscribe import Subscription


async def main():
    instance = EphyrInstance(ipv4="142.132.160.160", https=False)

    sub = Subscription(
        instance=instance,  # provides basic connection data
        method_call=api_subscribe_state,  # define what method to call
    )

    # Subscription object can be used to subscribe multiple times.
    await asyncio.gather(
        watch(sub),
        watch(sub),
        asyncio.sleep(5),
    )


async def watch(sub):
    # session() creates object that handles connect. it cannot be used in parallel
    async with sub.session() as s:
        # iterate() accepts variables, it provide async iterator
        async for upd in s.iterate():
            print(upd)
            # Idea: you can use library "deepdiff" to narrow down
            # which changes are important.


if __name__ == "__main__":
    asyncio.run(main())
