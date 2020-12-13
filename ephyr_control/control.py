import logging
from typing import Dict, Optional

import zmq

from .utils import is_open
from .config import (
    LangStreamConfig,
    SpecificStream,
    StreamConfig,
)

__all__ = ["EphyrStreamControl"]


class StreamCommunicator:
    @classmethod
    def create_org(cls, lang_code: str, config: LangStreamConfig):
        return cls(type="org", lang_code=lang_code, config=config.org)

    @classmethod
    def create_trn(cls, lang_code: str, config: LangStreamConfig):
        return cls(type="trn", lang_code=lang_code, config=config.trn)

    def __init__(self, type: str, lang_code: str, config: StreamConfig):
        self.type = type
        self.lang_code = lang_code
        self._config = config

        self.zmq_host = config.zmq.host
        self.zmq_port = config.zmq.port
        self.default_volume = config.volume
        self.default_delay = config.delay

        self.conn: Optional[zmq.Socket] = None
        self.curr_volume: Optional[float] = None
        self.vol_state: Optional[float] = None

    def __str__(self):
        return f"StreamCommunicator <{self.type}-{self.lang_code}: {self._config.ip_address}>"

    def volume(self, vol: float) -> bool:
        self.conn.send_string(f"volume@{self.type} volume {vol}")
        if self.conn.recv_string().endswith("Success"):
            self.curr_volume = vol
            return True
        return False

    @property
    def is_connected(self) -> bool:
        return bool(self.conn)

    def _create_conn(self):
        return create_conn(self.zmq_host, self.zmq_port)

    def connect(self) -> bool:
        self.conn = self._create_conn()
        self.to_default()
        return self.is_connected

    def to_default(self) -> bool:
        return self.volume(self.default_volume)

    def to_delay(self, delay: str):
        raise NotImplemented


class LangStreamControl:
    def __init__(
        self,
        lang_code: str,
        org: StreamCommunicator,
        trn: StreamCommunicator,
    ):
        self.lang_code = lang_code
        self.org = org
        self.trn = trn

    def connect(self):
        self.org.connect()
        self.trn.connect()
        logging.debug(f"{self} - connected")

    def disconnect(self):
        self.org.connect()
        self.trn.connect()
        logging.debug(f"{self} - disconnected")

    @property
    def is_connected(self):
        return self.org.is_connected and self.trn.is_connected

    def to_trn(self):
        self.trn.volume(1.0)
        self.org.volume(0.3)

    def to_org(self):
        self.trn.volume(0.0)
        self.org.volume(1.0)

    def mute_all(self):
        self.trn.vol_state = self.trn.curr_volume
        self.org.vol_state = self.org.curr_volume
        self.trn.volume(0.0)
        self.org.volume(0.0)

    def mute_org(self):
        self.org.vol_state = self.org.curr_volume
        self.org.volume(0.0)

    def mute_trn(self):
        self.trn.vol_state = self.trn.curr_volume
        self.trn.volume(0.0)

    def unmute_all(self):
        self.trn.volume(self.trn.vol_state)
        self.org.volume(self.org.vol_state)

    @classmethod
    def build(cls, lang_code: str, stream: LangStreamConfig):
        return cls(
            lang_code,
            StreamCommunicator.create_org(lang_code, stream),
            StreamCommunicator.create_trn(lang_code, stream),
        )

    def __repr__(self):
        return f"{self.lang_code.capitalize()} StreamControl"


class EphyrStreamControl:
    def __init__(
        self,
        lang_streams: Dict[str, LangStreamControl],
    ):
        self.lang_streams = lang_streams

    def connect(self):
        connection_errors = []
        for lang_code, lang_stream in self.lang_streams.items():
            try:
                lang_stream.connect()
            except ConnectionError as e:
                connection_errors.append(e)
        if connection_errors:
            raise ConnectionError(
                "Failed to connect to following hosts:\n{}".format(
                    "\n".join(str(e) for e in connection_errors)
                )
            )

    @property
    def active_connections(self) -> Dict[str, LangStreamControl]:
        return {
            code: stream
            for code, stream in self.lang_streams.items()
            if stream.is_connected
        }

    def __repr__(self):
        return f"EventStreamControl - <{self.lang_streams}>"

    def __iter__(self):
        yield from self.lang_streams.items()

    def __getitem__(self, item):
        return self.lang_streams[item]

    @classmethod
    def build(cls, config: SpecificStream):
        return cls(
            {
                lang_code: LangStreamControl.build(lang_code, stream)
                for lang_code, stream in config
            }
        )


def create_conn(server_address: str, port: int) -> zmq.Socket:
    if not is_open(server_address, port):
        raise ConnectionError(f"The address {server_address}:{port} isn't available")
    context = zmq.Context()
    conn = context.socket(zmq.REQ)
    conn.connect(f"tcp://{server_address}:{port}")
    return conn
