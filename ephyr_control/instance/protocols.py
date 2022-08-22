import abc
import dataclasses
from typing import Protocol, Any, Dict, Optional, ClassVar, Type, Collection

from graphql.language.ast import Document as GqlDocument

from ephyr_control.instance.constants import EphyrApiPaths

try:
    import gql.transport.requests
except ImportError:
    raise RuntimeError("You need to install 'gql' together with 'requests' lib.")

__all__ = (
    "EphyrInstanceProtocol",
    "RemoteEphyrInstanceProtocol",
    "AssignedMethodCall",
    "ServerConnectionDetails",
    "ClientNotInitialisedError",
    "AssignedClientProtocol",
    "ClientsCollectionProtocol",
    "RemoteEphyrInstanceProtocol",
)


class EphyrInstanceProtocol(Protocol):
    scheme: str
    ipv4: str
    host: str
    port: int
    password: Optional[str]


@dataclasses.dataclass
class AssignedMethodCall:
    api_path: EphyrApiPaths
    query: GqlDocument


@dataclasses.dataclass
class ServerConnectionDetails:
    scheme: str
    host: str
    port: int
    password: Optional[str] = None


class ClientNotInitialisedError(Exception):
    """Raised when Client was not yet initialised."""


class AssignedClientProtocol(Protocol):
    """Client assigned to API path - protocol."""

    api_path: EphyrApiPaths
    client: gql.Client = None

    Transport: ClassVar[Type[gql.transport.Transport]]

    ClientNotInitialisedError: ClassVar[Type[Exception]] = ClientNotInitialisedError

    def __post_init__(self):
        if not hasattr(self, "Transport"):
            raise NotImplementedError('Define "Transport" class variable')

    @property
    def is_initialised(self) -> bool:
        """

        :return:
        """
        return self.client is not None

    @abc.abstractmethod
    def rebuild_client(
        self, server_connection_details: ServerConnectionDetails
    ) -> None:
        """Rebuild GraphQL client.
        Useful when connection parameters change.

        :param server_connection_details: Details that specify how to connect to server
        :return:
        """

    @abc.abstractmethod
    def execute(
        self,
        method_call: AssignedMethodCall,
        variable_values: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Execute GraphQL query with optional variables.

        "raises ClientNotInitialisedError: if client was not yet initialised
        :raises ValueError: if passed method_call is assigned to another
        API path than client
        :param method_call: GraphQL query
        :param variable_values: dictionary for variables, optional
        :return: data returned from server
        """


class ClientsCollectionProtocol(Protocol):
    """Collection of clients - protocol.

    Work with multiple clients at once,
    execute method call without specified concrete client - only API path needed.
    """

    assigned_clients: Dict[EphyrApiPaths, AssignedClientProtocol]

    def __init__(self, clients: Collection[AssignedClientProtocol]):
        self.assigned_clients = {client.api_path: client for client in clients}

    def rebuild_all_clients(
        self, server_connection_details: ServerConnectionDetails
    ) -> None:
        """Rebuild GraphQL all clients.
        Useful when connection parameters change.

        :param server_connection_details: Details that specify how to connect to server
        :return:
        """
        for cli in self.assigned_clients.values():
            cli.rebuild_client(server_connection_details)

    def execute(
        self,
        method_call: AssignedMethodCall,
        variable_values: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Execute GraphQL query with optional variables.

        :raises KeyError: if there is no client matching API path for passed method_call
        :param method_call: GraphQL query
        :param variable_values: dictionary for variables, optional
        :return: data returned from server
        """
        client = self.assigned_clients.get(method_call.api_path)
        if client is None:
            raise KeyError(f"There is no client matching {method_call}")

        return client.execute(
            method_call=method_call,
            variable_values=variable_values,
        )


class RemoteEphyrInstanceProtocol(EphyrInstanceProtocol, Protocol):
    """EPhyr isntance hosted on server.

    Implements methods to communicate with Ephyr server."""

    clients: ClientsCollectionProtocol

    def get_connection_details(self) -> ServerConnectionDetails:
        """Create connection details object.

        :return: ServerConnectionDetails
        """
        return ServerConnectionDetails(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            password=self.password,
        )

    def rebuild_clients(self) -> None:
        """Rebuild all clients in collection.

        :return: None
        """
        self.clients.rebuild_all_clients(self.get_connection_details())

    def execute(
        self,
        method_call: AssignedMethodCall,
        variable_values: Optional[Dict[str, Any]] = None,
    ):
        """Execute GraphQL query with optional variables.

        :raises KeyError: if there is no client matching API path for passed method_call
        :param method_call: GraphQL query
        :param variable_values: dictionary for variables, optional
        :return: data returned from server
        """
        return self.clients.execute(
            method_call=method_call, variable_values=variable_values
        )

    @abc.abstractmethod
    def verify_ipv4_domain_match(self) -> bool:
        """
        Checks if provided IPv4 matches the actual one.
        :return:
        """
