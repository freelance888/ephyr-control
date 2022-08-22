import gql

from ephyr_control.instance.constants import EphyrApiPaths
from ephyr_control.instance.protocols import (
    AssignedMethodCall,
)

__all__ = (
    "api_get_info",
    "api_change_password",
    "api_change_settings",
    "api_change_state",
    "api_export_all_restreams",
    "dashboard_add_client",
    "dashboard_remove_client",
)


# main API queries
# ================

api_get_info = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
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
    ),
)

api_change_password = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
        """
        mutation ($new: String, $old: String, $kind: PasswordKind!) {
            setPassword(new: $new, old: $old, kind: $kind)
        }
    """
    ),
)

api_change_settings = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
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
    ),
)

api_change_state = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
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
    ),
)

api_export_all_restreams = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
        """
        query ExportAllRestreams {
            export
        }
    """
    ),
)


# Dashboard API queries
# =====================

dashboard_add_client = AssignedMethodCall(
    api_path=EphyrApiPaths.DASHBOARD,
    query=gql.gql(
        """
        mutation AddClient($client_id: ClientId!) {
            addClient(clientId: $client_id)
        }
        """
    ),
)

dashboard_remove_client = AssignedMethodCall(
    api_path=EphyrApiPaths.DASHBOARD,
    query=gql.gql(
        """
        mutation RemoveClient($client_id: ClientId!) {
            removeClient(clientId: $client_id)
        }
        """
    ),
)
