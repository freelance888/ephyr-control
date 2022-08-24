"""
API to subscribe for Ephyr servers.

Example usage:

"""

import dataclasses
from typing import Type, ClassVar, Optional, Dict, Any, AsyncIterator

import gql
import gql.transport
import graphql
import yarl

from ephyr_control.instance.protocols import EphyrInstanceProtocol, AssignedMethodCall

try:
    from gql.transport.websockets import WebsocketsTransport
except ImportError:
    raise RuntimeError("Install gql[websockets] extra")

__all__ = (
    "Subscription",
    "SubscriptionSession",
    "UpdatesIterator",
)


@dataclasses.dataclass(frozen=True)
class Subscription:
    instance: EphyrInstanceProtocol
    method_call: AssignedMethodCall
    use_ssl: Optional[bool] = None

    Transport: ClassVar[Type[gql.transport.AsyncTransport]] = WebsocketsTransport

    def __post_init__(self):
        if (
            self.method_call.operation_type
            != graphql.language.ast.OperationType.SUBSCRIPTION
        ):
            raise ValueError("Only accept subscription operations.")

    def build_ws_url(self) -> yarl.URL:
        if self.use_ssl is None:
            use_ssl = self.instance.scheme == "https"
        else:
            use_ssl = self.use_ssl
        scheme = "wss" if use_ssl else "ws"
        return yarl.URL.build(
            scheme=scheme,
            host=self.instance.host,
            password=self.instance.password,
            path=self.method_call.api_path.value,
        )

    def build_client(self) -> gql.Client:
        url = self.build_ws_url()
        transport = self.Transport(str(url))
        return gql.Client(transport=transport)

    def session(self) -> "SubscriptionSession":
        return SubscriptionSession(subscription=self, client=self.build_client())


@dataclasses.dataclass(frozen=True)
class SubscriptionSession:
    subscription: Subscription
    client: gql.Client

    async def __aenter__(self):
        session = await self.client.__aenter__()
        return UpdatesIterator(subscription=self.subscription, session=session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)


@dataclasses.dataclass(frozen=True)
class UpdatesIterator:
    subscription: Subscription
    session: gql.client.AsyncClientSession

    def iterate(
        self, variable_values: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[dict]:
        return self.session.subscribe(
            self.subscription.method_call.query,
            variable_values=variable_values,
        )
