import dataclasses
import json
import logging
import uuid
from typing import ClassVar, Type, Optional, Dict, Any, Tuple

import gql
import gql.transport.requests
import yarl

from ephyr_control.instance.constants import (
    EphyrApiPaths,
    ALL_API_PATHS,
    EphyrPasswordKind,
    MIXIN_UI_PATH,
)
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
    mixin_tune_volume,
    mixin_tune_delay,
    mixin_tune_sidechain,
    dashboard_add_client,
    dashboard_remove_client,
)
from ephyr_control.state.restream.output.volume import Volume
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

    def build_output_url(
        self,
        restream_id: uuid.UUID,
        output_id: uuid.UUID,
        output_password: Optional[str] = None,
    ) -> yarl.URL:
        """
        Construct URL for concrete Output UI page.
        :param restream_id: uuid of Restream
        :param output_id: uuid of Output
        :param output_password: optional, provide password if it is set for Output UI
        :return:
        """
        # use more verbose UUID format because this URL might be used by users
        query = {
            "id": str(restream_id),
            "output": str(output_id),
        }
        base = self.build_url().with_path(MIXIN_UI_PATH).with_query(query)

        if output_password:
            # override auth
            return base.with_password(output_password).with_user(
                self.DEFAULT_USER_HTTPAUTH
            )
        else:
            # remove user because there's no password
            return base.with_password(None).with_user(None)


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

    def change_password(
        self,
        new_password: str or None,
    ) -> bool:
        """
        Change password. Set to None to remove password protection.
        :param new_password: string of new password (as user types it), set
        None to remove password protection
        :return: success
        """
        variables = {
            "new": new_password,
            "old": self.password,
            "kind": EphyrPasswordKind.MAIN.value,
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
        Change state (includes settings and restreams) of the Ephyr instance.
        :param state: State object
        :param replace: if True, server will try to match objects and update their
        configuration, otherwise - replace entire State.
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

    def export(self) -> dict:
        """
        Export Ephyr server data (includes restreams and settings).
        :return: dict with data
        """
        data = self.execute(api_export_all_restreams)
        as_string = data["export"]
        return json.loads(as_string)

    def add_instance_to_dashboard(
        self,
        instance: RemoteEphyrInstanceProtocol,
    ) -> bool:
        """Add another instance to Dashboard UI.

        :param instance: Ephyr instance to add to dashboard
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

        :param instance: Ephyr instance to remove from dashboard
        :return: success status
        """
        variables = {
            "client_id": str(instance.build_url()),
        }
        response = self.execute(dashboard_remove_client, variable_values=variables)
        return response["removeClient"]

    def tune_volume(
        self,
        restream_id: uuid.UUID,
        output_id: uuid.UUID,
        volume: Volume,
        mixin_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """
        Set volume options for output's main source or one of it's mixins.
        :param restream_id: uuid of Restream
        :param output_id: uuid of Output
        :param mixin_id: optional, if None - applies for main source (e.g. not a mixin)
        :param volume: Volume object containing
        :return: success
        """
        variables = {
            "restream_id": restream_id.hex,
            "output_id": output_id.hex,
            "mixin_id": mixin_id.hex,
            "level": volume.level,
            "muted": volume.muted,
        }
        response = self.execute(mixin_tune_volume, variable_values=variables)
        return response["tuneVolume"]

    def tune_delay(
        self,
        restream_id: uuid.UUID,
        output_id: uuid.UUID,
        mixin_id: uuid.UUID,
        delay_milliseconds: int,
    ) -> bool:
        """
        Set delay option for output's mixin.
        :param restream_id: uuid of Restream
        :param output_id: uuid of Output
        :param mixin_id: uuid of Mixin
        :param delay_milliseconds: delay in milliseconds, controls by how much
        mixin stream will be delayed relatively to main stream.
        :return: success
        """
        variables = {
            "restream_id": restream_id.hex,
            "output_id": output_id.hex,
            "mixin_id": mixin_id.hex,
            "delay": delay_milliseconds,
        }
        response = self.execute(mixin_tune_delay, variable_values=variables)
        return response["tuneDelay"]

    def tune_sidechain(
        self,
        restream_id: uuid.UUID,
        output_id: uuid.UUID,
        mixin_id: uuid.UUID,
        sidechain_enabled: bool,
    ) -> bool:
        """
        Set sidechain option for output's mixin.
        :param restream_id: uuid of Restream
        :param output_id: uuid of Output
        :param mixin_id: uuid of Mixin
        :param sidechain_enabled: state of sidechain feature
        :return: success
        """
        variables = {
            "restream_id": restream_id.hex,
            "output_id": output_id.hex,
            "mixin_id": mixin_id.hex,
            "sidechain": sidechain_enabled,
        }
        response = self.execute(mixin_tune_sidechain, variable_values=variables)
        return response["tuneSidechain"]
