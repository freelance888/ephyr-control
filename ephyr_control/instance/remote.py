import dataclasses
import logging
from typing import ClassVar, Type, Optional, Dict, Any, Tuple

import gql
import gql.transport.requests
import yarl

from ephyr_control.instance.constants import EphyrApiPaths, ALL_API_PATHS
from ephyr_control.instance.instance import EphyrInstance
from ephyr_control.instance.protocols import (
    RemoteEphyrInstanceProtocol,
    ServerConnectionDetails,
    AssignedClientProtocol,
    ClientsCollectionProtocol,
    AssignedMethodCall,
)
from ephyr_control.instance.queries import (
    api_change_settings,
    api_change_state,
    api_change_password,
    api_get_info,
    api_export_all_restreams,
    dashboard_add_client,
    dashboard_remove_client,
)
from ephyr_control.state.settings import Settings
from ephyr_control.state.state import State
from ephyr_control.utils.pinger import Pinger

__all__ = (
    "AssignedClient",
    "ClientsCollection",
    "BaseRemoteEphyrInstance",
    "RemoteEphyrInstance",
)


@dataclasses.dataclass
class AssignedClient(AssignedClientProtocol):
    api_path: EphyrApiPaths
    client: gql.Client = None

    Transport: ClassVar[
        Type[gql.transport.Transport]
    ] = gql.transport.requests.RequestsHTTPTransport

    def rebuild_client(
        self, server_connection_details: ServerConnectionDetails
    ) -> None:
        url = yarl.URL.build(
            scheme=server_connection_details.scheme,
            host=server_connection_details.host,
            password=server_connection_details.password or "",
            path=self.api_path.value,
        )

        transport = self.Transport(url=str(url))
        self.client = gql.Client(transport=transport)

    def execute(
        self,
        method_call: AssignedMethodCall,
        variable_values: Optional[Dict[str, Any]] = None,
    ) -> dict:
        if not self.is_initialised:
            raise self.ClientNotInitialisedError(
                "Client was not initialised yet. Call rebuild_client method."
            )

        if self.api_path != method_call.api_path:
            raise ValueError("api_path does not match")

        return self.client.execute(
            method_call.query,
            variable_values=variable_values,
        )


@dataclasses.dataclass
class ClientsCollection(ClientsCollectionProtocol):
    clients: Tuple[AssignedClientProtocol, ...]
    assigned_clients: Dict[EphyrApiPaths, AssignedClientProtocol] = dataclasses.field(
        init=False
    )

    def __post_init__(self):
        self.assigned_clients = {client.api_path: client for client in self.clients}


@dataclasses.dataclass
class BaseRemoteEphyrInstance(EphyrInstance, RemoteEphyrInstanceProtocol):
    """Base class implementing RemoteEphyrInstanceProtocol"""

    connect_to: Tuple[EphyrApiPaths, ...] = ALL_API_PATHS

    # username used for BasicAuth, 1 is well accepted by browsers
    DEFAULT_USER_HTTPAUTH: str = "1"

    def __post_init__(self):
        self.clients = ClientsCollection(
            tuple(AssignedClient(api) for api in self.connect_to)
        )
        self.rebuild_clients()

    def ping(
        self,
        do_raise: bool = False,
        check_domain: bool = True,
        loglevel: str = logging.ERROR,
    ) -> bool:
        if check_domain:
            if not self.domain:
                raise ValueError("Can not check domain if it is not set")
            host = self.domain
        else:
            host = self.host
        pinger = Pinger(
            host=host,
            protocol=self.scheme,
            do_raise=do_raise,
            do_report_error=True,
            loglevel=loglevel,
            password=self.password,
        )
        return pinger.ping()

    def build_url(self, dashboard: bool = False) -> yarl.URL:
        # TODO: add arguments to connect to mixin output
        connection_details = self.get_connection_details()
        if dashboard:
            path = "/dashboard"
        else:
            path = "/"
        return yarl.URL.build(
            scheme=connection_details.scheme,
            user=self.DEFAULT_USER_HTTPAUTH if connection_details.password else None,
            password=connection_details.password,
            host=connection_details.host,
            port=connection_details.port,
            path=path,
        )


@dataclasses.dataclass
class RemoteEphyrInstance(BaseRemoteEphyrInstance):
    """Implements concrete actions on Ephyr server."""

    def get_info(self) -> dict:
        """
        Get basic info about instance (title, publicHost, some settings)
        :return: dictionary
        """
        data = self.execute(api_get_info)
        return data["info"]

    def verify_ipv4_domain_match(self) -> bool:
        public_host = self.get_info()["publicHost"]
        return public_host == self.ipv4

    def change_password(self, new_password: str or None) -> bool:
        """
        Change password. Set to None to remove password protection.
        :param new_password: string of new password (as user types it), set
        None to remove password protection
        :return: success
        """
        variables = {
            "new": new_password,
            "old": self.password,
            "kind": "MAIN",
        }
        response = self.execute(
            api_change_password,
            variable_values=variables,
        )
        success: bool = response["setPassword"]
        if success:
            self.password = new_password
            self.rebuild_clients()
        return success

    def change_settings(self, settings: Settings) -> bool:
        """
        Change only settings of the Ephyr instance.
        :param settings: Settings object
        :return: success
        """
        variables = settings.to_dict()
        response = self.execute(
            api_change_settings,
            variable_values=variables,
        )
        return response["setSettings"]

    def change_state(self, state: State, replace: bool = False) -> bool:
        """
        Change state (includes settings and restreams) of the Ephyr isntance.
        :param state: State object
        :param replace: # FIXME
        :return: success
        """
        variables = {
            "restream_id": None,
            "replace": replace,
            "spec": state.to_json(cleanup=True, prettify=False),
        }
        response = self.execute(
            api_change_state,
            variable_values=variables,
        )
        return response["import"]

    def export_all_restreams_raw(self) -> str:
        """
        Export all restreams' data in as string JSON.
        :return: JSON string
        """
        data = self.execute(api_export_all_restreams)
        return data["export"]

    def add_instance_to_dashboard(
        self,
        instance: RemoteEphyrInstanceProtocol,
    ) -> bool:
        """Add another instance to Dashboard UI.

        :return: success status
        """
        variables = {
            "client_id": str(instance.build_url()),
        }
        response = self.execute(dashboard_add_client, variable_values=variables)
        return response["addClient"]

    def remove_instance_from_dashboard(
        self,
        instance: RemoteEphyrInstanceProtocol,
    ) -> bool:
        """Remove another instance from Dashboard UI

        :return: success status
        """
        variables = {
            "client_id": str(instance.build_url()),
        }
        response = self.execute(dashboard_remove_client, variable_values=variables)
        return response["removeClient"]
