"""
API to subscribe for Ephyr servers.
Unlike most of the lib, it is developed for use in asyncio environment.

See example usage in examples/subscribe.py
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
    """
    Subscription manager for concrete Ephyr instance.
    Does not update already created sessions.
    Operates using websockets.

    :param instance: provides connection options
    :param method_call: defines GraphQL operation and API (path) to use
    :param use_ssl: overrides SSL on/off settings provided by EphyrInstance
    """

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
        """
        Build URL for websocket connection.
        :return: yarl.URL
        """
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

    def build_transport(self, url: yarl.URL) -> gql.transport.AsyncTransport:
        """
        Build AsyncTransport object.
        :param url:
        :return:
        """
        return self.Transport(
            str(url),
            connect_args={
                # Ephyr server does not support ping at the moment
                "ping_interval": None,
            },
        )

    def build_client(self) -> gql.Client:
        """
        Builds gql Client
        :return: gql.Client
        """
        url = self.build_ws_url()
        transport = self.build_transport(url=url)
        return gql.Client(transport=transport)

    def session(self) -> "SubscriptionSession":
        """
        Create SubscriptionSession which is not updated by instance changes.
        Separate object being created with standalone gql.Client to allow changes
        made in EphyrInstance to apply to gql.Client.
        :return: session object
        """
        return SubscriptionSession(subscription=self, client=self.build_client())


@dataclasses.dataclass(frozen=True)
class SubscriptionSession:
    """
    Session for subscription operation.
    Does not react to changes in subscription.instance object
    Acts as async context manager - manages connection to server.
    Returns UpdatesIterator upon entering context.

    This is a separate class from Subscription with standalone gql.Client because
    it allows changes made in EphyrInstance to apply to gql.Client.
    """

    subscription: Subscription
    client: gql.Client

    async def __aenter__(self):
        session = await self.client.__aenter__()
        return UpdatesIterator(subscription=self.subscription, session=session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)


@dataclasses.dataclass(frozen=True)
class UpdatesIterator:
    """
    Executes operation and iterates data.
    Stores all required information to subscribe without repeating.
    """

    subscription: Subscription
    session: gql.client.AsyncClientSession

    def iterate(
        self, variable_values: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[dict]:
        """
        Executes operation and iterates data.
        :param variable_values: dict of variables used in GraphQl
        subscription operation.
        :return:
        """
        return self.session.subscribe(
            self.subscription.method_call.query,
            variable_values=variable_values,
        )
