import dataclasses
import logging
from typing import ClassVar, Type

import gql
import gql.transport.requests

from .instance import EphyrInstance
from .. import State, Settings
from ..utils import Pinger

__all__ = ("RemoteEphyrInstance",)


@dataclasses.dataclass
class RemoteEphyrInstance(EphyrInstance):
    _client: gql.Client = None

    EPHYR_GRAPHQL_URL_TEMPLATE: ClassVar[str] = "{scheme}://:{password}@{host}/api"

    Transport: ClassVar[Type] = gql.transport.requests.RequestsHTTPTransport

    @property
    def client(self) -> gql.Client:
        if not self._client:
            self._client = self._build_client()
        return self._client

    def _build_remote_url(self) -> str:
        return self.EPHYR_GRAPHQL_URL_TEMPLATE.format(
            scheme=self.scheme,
            host=self.host,
            password=self.password or "",
        )

    def _build_client(self) -> gql.Client:
        url = self._build_remote_url()
        transport = self.Transport(url=url)
        return gql.Client(transport=transport)

    def execute(self, query: gql.gql, variable_values: dict = None):
        return self.client.execute(
            query,
            variable_values=variable_values,
        )

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

    gql_change_password = gql.gql(
        """
        mutation ($new: String, $old: String, $kind: PasswordKind!) {
            setPassword(new: $new, old: $old, kind: $kind)
        }
    """
    )

    def _change_password(self, new_password: str or None) -> dict:
        return self.execute(
            self.gql_change_password,
            variable_values={"new": new_password, "old": self.password, "kind": "MAIN"},
        )

    def change_password(self, new_password: str or None) -> bool:
        response = self._change_password(new_password=new_password)
        success = response["setPassword"]
        if success:
            self.password = new_password
            self._client = self._build_client()
        return success

    gql_change_settings = gql.gql(
        """
        mutation SetSettings(
            $title: String
            $delete_confirmation: Boolean!
            $enable_confirmation: Boolean!
        ) {
            setSettings(
                title: $title
                deleteConfirmation: $delete_confirmation
                enableConfirmation: $enable_confirmation
            )
        }
    """
    )

    def _change_settings(self, settings: Settings) -> dict:
        variables = settings.to_dict()
        return self.execute(
            self.gql_change_settings,
            variable_values=variables,
        )

    def change_settings(self, settings: Settings) -> bool:
        result = self._change_settings(settings=settings)
        success = result["setSettings"]
        return success

    gql_change_state = gql.gql(
        """
        mutation Import(
            $restream_id: RestreamId
            $replace: Boolean!
            $spec: String!
        ) {
            import(
                restreamId: $restream_id
                replace: $replace
                spec: $spec
            )
        }
    """
    )

    def _change_state(self, state: State, replace: bool = False) -> dict:
        variables = dict(
            restream_id=None,
            replace=replace,
            spec=state.to_json(cleanup=True, prettify=False),
        )
        return self.execute(
            self.gql_change_state,
            variable_values=variables,
        )

    def change_state(self, state: State, replace: bool = False) -> bool:
        result = self._change_state(state=state, replace=replace)
        success = result["import"]
        return success

    gql_get_info = gql.gql(
        """
        query Info {
            info {
                publicHost
                title
                passwordHash
                passwordOutputHash
                deleteConfirmation
                enableConfirmation
            }
        }
    """
    )

    def get_info(self) -> dict:
        data = self.execute(self.gql_get_info)
        return data["info"]

    gql_export_all_restreams = gql.gql(
        """
        query ExportAllRestreams {
            export
        }
    """
    )

    def _export_all_restreams(self) -> dict:
        data = self.execute(self.gql_export_all_restreams)
        return data["export"]

    def verify_ipv4_domain_match(self) -> bool:
        public_host = self.get_info()["publicHost"]
        return public_host == self.ipv4
