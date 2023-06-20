import asyncio
import ipaddress
import os
from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Union

import deepdiff

from ephyr_control.custom_typing import IPv4

try:
    import aiofiles
    import orjson as json
except ImportError:
    print("dump_state functionality is not active")

from .instance import RemoteEphyrInstance
from .instance.queries import api_subscribe_to_state
from .instance.subscribe import Subscription
from .types import EphyrConfig, EphyrConfigFull

__all__ = [
    "subscribe",
    "get_ephyr_state",
]
_state_lock = Lock()
_SUBSCRIPTION_STATE: Dict[IPv4, EphyrConfigFull] = {}
_CUR_DIR = Path(os.getcwd())


def _set_ephyr_state(ipv4: IPv4, config: EphyrConfigFull):
    with _state_lock:
        _SUBSCRIPTION_STATE[ipv4] = config


def get_ephyr_state(ipv4: IPv4) -> EphyrConfigFull:
    with _state_lock:
        return _SUBSCRIPTION_STATE[ipv4]


def get_state_values() -> List[EphyrConfig]:
    with _state_lock:
        return list(_SUBSCRIPTION_STATE.values())


def subscribe_to_ephyr_state_change(ephyr_config: EphyrConfig) -> Subscription:
    instance = RemoteEphyrInstance.from_config(ephyr_config)
    sub = Subscription(
        instance=instance,  # provides basic connection data
        method_call=api_subscribe_to_state,  # define what method to call
    )
    return sub


def extract_ephyrs_info(input_path: Path) -> List[EphyrConfig]:
    with open(input_path, "r") as f:
        return json.loads(f.read())


async def dump_state(state: dict, state_path: Path):
    while True:
        async with aiofiles.open(state_path, "wb") as f:
            await f.write(json.dumps(state))
        await asyncio.sleep(1)


async def update_state(sub):
    # session() creates object that handles connect. it cannot be used in parallel
    async with sub.session() as s:
        # iterate() accepts variables, it provides async iterator
        async for upd in s.iterate():
            prev_state = deepcopy(_SUBSCRIPTION_STATE)
            _set_ephyr_state(
                sub.instance.ipv4,
                EphyrConfigFull(
                    ipv4=sub.instance.ipv4,
                    title=sub.instance.title,
                    domain=sub.instance.domain,
                    password=sub.instance.password,
                    restreams=upd["allRestreams"],
                ),
            )

            difference = deepdiff.DeepDiff(prev_state, _SUBSCRIPTION_STATE)
            if difference:
                print(difference.pretty())


def verify_ephyrs_config(configs: List[EphyrConfig]):
    """Verify that no duplicate of `title` or `ipv4` in configuration"""
    items = defaultdict(int)
    for info in configs:
        items[info["ipv4"]] += 1
        title = info.get("title")
        if title:
            items[title] += 1
    errors = [key for key, val in items.items() if val > 1]
    if errors:
        raise ValueError(f"Ephyr config contains duplicate of: {errors}")


async def run_subscription(
    ephyrs_config: List[EphyrConfig], state_path: Optional[Path] = None
):
    subscriptions = [
        subscribe_to_ephyr_state_change(config) for config in ephyrs_config
    ]
    subscribed_servers = [
        c["domain"] if c.get("domain") else c["ipv4"] for c in ephyrs_config
    ]
    print(f"Subscribed to: {subscribed_servers}")
    processes = [update_state(sub) for sub in subscriptions]
    if state_path:
        processes.append(
            dump_state(_SUBSCRIPTION_STATE, state_path),
        )

    await asyncio.gather(
        *processes,
        asyncio.sleep(1),
        return_exceptions=True,
    )


def subscribe(ephyr_configs: List[EphyrConfig], state_path: Optional[Path] = None):
    verify_ephyrs_config(ephyr_configs)
    asyncio.run(
        run_subscription(ephyr_configs, state_path),
    )


def cli_parser():
    # type: () -> ArgumentParser

    parser = ArgumentParser(
        prog="ephyr_subscriber",
        description="Allow to write Ephyr instances state changes to local json",
    )

    # main params
    parser.add_argument(
        "input",
        help="The ephyr config file or IP address",
    )

    parser.add_argument(
        "-o",
        "--state_output",
        nargs="?",
        default="state.json",
        help="Path to file to save state output",
    )
    return parser


def to_ephyr_config_from_input(input: Union[Path, str]) -> List[EphyrConfig]:
    try:
        ipv4 = input
        # verify that ip address is correct
        ipaddress.ip_address(ipv4)
        return [dict(ipv4=input)]
    except ValueError:
        # it's not IP address or address is incorrect
        ...

    input = Path(input)
    # try to resolve as Path to ephyr config
    if not input.absolute():
        input = _CUR_DIR / input

    if not input.suffix == ".json":
        raise ValueError("Incorrect input file extension")
    if not input.exists():
        raise ValueError(f"Not found ephyr config on {input}")

    config = extract_ephyrs_info(input)
    verify_ephyrs_config(config)
    return config


def run_cli():
    args = cli_parser().parse_args()

    ephyr_config = to_ephyr_config_from_input(args.input)

    state_output = args.state_output
    if not state_output.endswith(".json"):
        raise ValueError("Incorrect state_output file extension")

    state_path = _CUR_DIR / state_output

    subscribe(ephyr_config, state_path)


if __name__ == "__main__":
    run_cli()
