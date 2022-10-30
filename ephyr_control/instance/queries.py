import gql

from ephyr_control.instance.constants import EphyrApiPaths
from ephyr_control.instance.protocols import AssignedMethodCall

__all__ = (
    "api_get_info",
    "api_change_password",
    "api_change_settings",
    "api_change_state",
    "api_export_all_restreams",
    "api_subscribe_to_state",
    "api_subscribe_to_info",
    "api_subscribe_to_server_info",
    "mixin_tune_volume",
    "mixin_tune_delay",
    "mixin_tune_sidechain",
    "mixin_subscribe_to_output",
    "dashboard_add_client",
    "dashboard_remove_client",
    "dashboard_subscribe_to_statistics",
)


# main API
# ========

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

api_subscribe_to_state = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
        """
        subscription State {
            allRestreams {
                id
                key
                label
                input {
                    id
                    key
                    endpoints {
                        id
                        kind
                        status
                        label
                    }
                    src {
                        ... on RemoteInputSrc {
                            url
                            label
                        }
                        ... on FailoverInputSrc {
                            inputs {
                                id
                                key
                                endpoints {
                                    id
                                    kind
                                    status
                                    label
                                }
                                src {
                                    ... on RemoteInputSrc {
                                        url
                                        label
                                    }
                                }
                                enabled
                            }
                        }
                    }
                    enabled
                }
                outputs {
                    id
                    dst
                    label
                    previewUrl
                    volume {
                        level
                        muted
                    }
                    mixins {
                        id
                        src
                        volume {
                            level
                            muted
                        }
                        delay
                        sidechain
                    }
                    enabled
                    status
                }
            }
        }
        """
    ),
)

api_subscribe_to_info = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
        """
        subscription Info {
            info {
                publicHost
                title
                deleteConfirmation
                enableConfirmation
                passwordHash
                passwordOutputHash
            }
        }
        """
    ),
)

api_subscribe_to_server_info = AssignedMethodCall(
    api_path=EphyrApiPaths.API,
    query=gql.gql(
        """
        subscription ServerInfo {
            serverInfo {
                cpuUsage
                ramTotal
                ramFree
                txDelta
                rxDelta
                errorMsg
            }
        }
        """
    ),
)


# output mixin API
# ================

mixin_tune_volume = AssignedMethodCall(
    api_path=EphyrApiPaths.MIXIN,
    query=gql.gql(
        """
        mutation TuneVolume(
            $restream_id: RestreamId!
            $output_id: OutputId!
            $mixin_id: MixinId
            $level: VolumeLevel!
            $muted: Boolean!
        ) {
            tuneVolume(
                restreamId: $restream_id
                outputId: $output_id
                mixinId: $mixin_id
                level: $level
                muted: $muted
            )
        }
        """
    ),
)

mixin_tune_delay = AssignedMethodCall(
    api_path=EphyrApiPaths.MIXIN,
    query=gql.gql(
        """
        mutation TuneDelay(
            $restream_id: RestreamId!
            $output_id: OutputId!
            $mixin_id: MixinId!
            $delay: Delay!
        ) {
            tuneDelay(
                restreamId: $restream_id
                outputId: $output_id
                mixinId: $mixin_id
                delay: $delay
            )
        }
        """
    ),
)

mixin_tune_sidechain = AssignedMethodCall(
    api_path=EphyrApiPaths.MIXIN,
    query=gql.gql(
        """
        mutation TuneSidechain(
            $restream_id: RestreamId!
            $output_id: OutputId!
            $mixin_id: MixinId!
            $sidechain: Boolean!
        ) {
            tuneSidechain(
                restreamId: $restream_id
                outputId: $output_id
                mixinId: $mixin_id
                sidechain: $sidechain
            )
        }
        """
    ),
)

mixin_subscribe_to_output = AssignedMethodCall(
    api_path=EphyrApiPaths.MIXIN,
    query=gql.gql(
        """
        subscription Output($restreamId: RestreamId!, $outputId: OutputId!) {
            output(outputId: $outputId, restreamId: $restreamId) {
                id
                dst
                label
                previewUrl
                volume {
                    level
                    muted
                }
                mixins {
                    id
                    src
                    volume {
                        level
                        muted
                    }
                    delay
                    sidechain
                }
                enabled
                status
            }
        }
        """
    ),
)


# Dashboard API
# =============

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

dashboard_subscribe_to_statistics = AssignedMethodCall(
    api_path=EphyrApiPaths.DASHBOARD,
    query=gql.gql(
        """
        subscription Statistics {
            statistics {
                id
                statistics {
                    data {
                        clientTitle
                        timestamp
                        inputs {
                            status
                            count
                        }
                        outputs {
                            status
                            count
                        }
                        serverInfo {
                            cpuUsage
                            ramTotal
                            ramFree
                            txDelta
                            rxDelta
                            errorMsg
                        }
                    }
                    errors
                }
            }
        }
        """
    ),
)
