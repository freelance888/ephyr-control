from unittest.mock import Mock

import pytest
from zmq import Socket

from ephyr_control import __version__, EphyrStreamControl
from ephyr_control.config import LangStreamConfig, StreamConfig, ZMQConfig
from ephyr_control.control import StreamCommunicator, LangStreamControl


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture
def lang_stream_config():
    org = StreamConfig(
        delay="0s", volume=0.5, zmq=ZMQConfig(host="0.0.0.0", port=60010)
    )
    trn = StreamConfig(
        delay="0s", volume=1.0, zmq=ZMQConfig(host="0.0.0.0", port=60020)
    )
    return LangStreamConfig(org=org, trn=trn)


@pytest.fixture
def lang_stream_control(lang_stream_config):
    org = StreamCommunicator.create_org("ru", lang_stream_config)
    trn = StreamCommunicator.create_trn("ru", lang_stream_config)

    mock_conn = Mock(Socket)
    mock_conn.recv_string = lambda: "1 Success"
    org._create_conn = Mock(return_value=mock_conn)
    trn._create_conn = Mock(return_value=mock_conn)
    lsc = LangStreamControl("ru", org, trn)
    lsc.connect()
    return lsc


@pytest.fixture
def ephyr_stream_control(lang_stream_control):
    return EphyrStreamControl({"ru": lang_stream_control, "en": lang_stream_control})


def test_volume_mute_and_unmute(lang_stream_control):
    lang_stream_control.trn.curr_volume = 1.0
    lang_stream_control.org.curr_volume = 0.3

    lang_stream_control.mute_all()
    assert lang_stream_control.trn.curr_volume == 0.0
    assert lang_stream_control.org.curr_volume == 0.0

    lang_stream_control.unmute_all()
    assert lang_stream_control.trn.curr_volume == 1.0
    assert lang_stream_control.org.curr_volume == 0.3


def test_ephyr_stream_control_iteration(ephyr_stream_control):
    assert ["ru", "en"] == list(ephyr_stream_control)
