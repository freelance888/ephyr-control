import dataclasses
import json
import logging
import uuid
from typing import Any, ClassVar, Dict, Optional, Tuple, Type, Union

import gql
import gql.transport.requests
import yarl

from ephyr_control.custom_typing import UUID4
from ephyr_control.instance.constants import (
    ALL_API_PATHS,
    MIXIN_UI_PATH,
    EphyrApiPaths,
    EphyrPasswordKind,
)
from ephyr_control.instance.instance import EphyrInstance
from ephyr_control.instance.protocols import (
    AssignedClientProtocol,
    AssignedMethodCall,
    ClientsCollectionProtocol,
    RemoteEphyrInstanceProtocol,
    ServerConnectionDetails,
)
from ephyr_control.instance.queries import (
    api_change_password,
    api_change_settings,
    api_change_state,
    api_disable_output,
    api_enable_output,
    api_export_all_restreams,
    api_get_info,
    api_remove_output,
    api_remove_restream,
    api_set_output,
    api_set_restream,
    dashboard_add_client,
    dashboard_remove_client,
    mixin_tune_delay,
    mixin_tune_sidechain,
    mixin_tune_volume,
)
from ephyr_control.state.restream.input import FailoverInput
from ephyr_control.state.restream.output import Volume
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
        loglevel: int = logging.ERROR,
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


@dataclasses.dataclass(unsafe_hash=True)
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

    def set_restream(
        self,
        key: str,
        url: Union[str, None] = None,
        label: Union[str, None] = None,
        with_hls=False,
        backup_inputs: [FailoverInput] or None = None,
        restream_id: Union[UUID4, str, None] = None,
    ) -> bool:
        """
        Add or update Restream input.
        :param key: string of stream key
        :param url: optional RTMP or HLS url if pull input needed
        :param label: optional string of Restream label
        :param with_hls: boolean value indicates that need stream of HLS
        :param backup_inputs: optional if addition backup input is required
        :param restream_id: optional UUID4 id if edit action is happening
        :return:
        """
        variables = {
            "key": key,
            "with_hls": with_hls,
        }
        if label:
            variables.update({"label": label})
        if restream_id:
            variables.update({"id": str(restream_id)})
        if url:
            variables.update({"url": url})
        # FIXME: need to add proper types here
        # if backup_inputs:
        #     variables.update({'backupInputs': backup_inputs})
        response = self.execute(
            api_set_restream,
            variable_values=variables,
        )
        success: bool = response["setRestream"]
        if success:
            self.rebuild_clients()
        return success

    def set_output(
        self,
        restream_id: Union[UUID4, str],
        url: Union[str, None] = None,
        label: Union[str, None] = None,
        preview_url: Union[str, None] = None,
        mixins: [str] or None = None,
        output_id: Union[UUID4, str, None] = None,
    ) -> bool:
        """
        Add or update Restream output.
        :param restream_id: uuid of Restream
        :param url: optional RTMP or HLS url if pull input needed
        :param label: optional string of Restream Output label
        :param preview_url: optional string of Restream Output preview
        :param mixins: list of mixin urls
        :param output_id: optional UUID4 id if edit action is happeing
        :return:
        """
        variables = {
            "restream_id": str(restream_id),
            "mixins": [],
        }
        if label:
            variables.update({"label": label})
        if output_id:
            variables.update({"id": str(output_id)})
        if url:
            variables.update({"url": url})
        if preview_url:
            variables.update({"preview_url": preview_url})
        if mixins:
            variables["mixins"].extend(mixins)
        response = self.execute(
            api_set_output,
            variable_values=variables,
        )
        success: bool = response["setOutput"]
        if success:
            self.rebuild_clients()
        return success

    def enable_output(
        self,
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str, None],
    ) -> bool:
        """
        Enable Restream Output.
        :param restream_id: UUID4 of Restream
        :param output_id: UUID4 id of Output
        :return:
        """
        variables = {
            "restream_id": str(restream_id),
            "output_id": str(output_id),
        }
        response = self.execute(
            api_enable_output,
            variable_values=variables,
        )
        success: bool = response["enableOutput"]
        if success:
            self.rebuild_clients()
        return success

    def disable_output(
        self,
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str, None],
    ) -> bool:
        """
        Disable Restream Output.
        :param restream_id: UUID4 of Restream
        :param output_id: UUID4 id of Output
        :return:
        """
        variables = {
            "restream_id": str(restream_id),
            "output_id": str(output_id),
        }
        response = self.execute(
            api_disable_output,
            variable_values=variables,
        )
        success: bool = response["disableOutput"]
        if success:
            self.rebuild_clients()
        return success

    def remove_output(
        self,
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str, None],
    ) -> bool:
        """
        Remove Restream Output.
        :param restream_id: UUID4 of Restream
        :param output_id: UUID4 id of Output
        :return:
        """
        variables = {
            "restream_id": str(restream_id),
            "output_id": str(output_id),
        }
        response = self.execute(
            api_remove_output,
            variable_values=variables,
        )
        success: bool = response["removeOutput"]
        if success:
            self.rebuild_clients()
        return success

    def remove_restream(
        self,
        restream_id: Union[UUID4, str],
    ) -> bool:
        """
        Remove Restream Output.
        :param restream_id: UUID4 of Restream
        :return:
        """
        variables = {
            "id": str(restream_id),
        }
        response = self.execute(
            api_remove_restream,
            variable_values=variables,
        )
        success: bool = response["removeRestream"]
        if success:
            self.rebuild_clients()
        return success

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
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str],
        volume: Volume,
        mixin_id: Optional[Union[UUID4, str]] = None,
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
            "restream_id": str(restream_id),
            "output_id": str(output_id),
            "level": volume.level,
            "muted": volume.muted,
        }
        if mixin_id:
            variables["mixin_id"] = str(mixin_id)
        response = self.execute(mixin_tune_volume, variable_values=variables)
        return response["tuneVolume"]

    def tune_delay(
        self,
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str],
        mixin_id: Union[UUID4, str],
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
            "restream_id": str(restream_id),
            "output_id": str(output_id),
            "mixin_id": str(mixin_id),
            "delay": delay_milliseconds,
        }
        response = self.execute(mixin_tune_delay, variable_values=variables)
        return response["tuneDelay"]

    def tune_sidechain(
        self,
        restream_id: Union[UUID4, str],
        output_id: Union[UUID4, str],
        mixin_id: Union[UUID4, str],
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
            "restream_id": str(restream_id),
            "output_id": str(output_id),
            "mixin_id": str(mixin_id),
            "sidechain": sidechain_enabled,
        }
        response = self.execute(mixin_tune_sidechain, variable_values=variables)
        return response["tuneSidechain"]
