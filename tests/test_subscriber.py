import json

import pytest

from ephyr_control.subscriber import to_ephyr_config_from_input


@pytest.mark.parametrize("input", ["123.444.444.555", "config_path", "config.json"])
def test_to_ephyr_config_with_incorrect_input(input):
    with pytest.raises(ValueError):
        to_ephyr_config_from_input(input)


@pytest.mark.parametrize(
    "input,result",
    [
        ("127.0.0.1", [{"ipv4": "127.0.0.1"}]),
    ],
)
def test_to_ephyr_config_with_correct_ipv4(input, result):
    assert to_ephyr_config_from_input(input) == result


@pytest.mark.parametrize(
    "config",
    [
        [{"ipv4": "127.0.0.1"}],
        [
            {
                "ipv4": "127.0.0.1",
                "title": "Some",
                "domain": "domain.com",
                "password": "password",
            }
        ],
    ],
)
def test_to_ephyr_config_with_correct_json(config, tmp_path):
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        f.write(json.dumps(config))
    assert to_ephyr_config_from_input(config_path) == config


@pytest.mark.parametrize(
    "config",
    [
        [
            {
                "ipv4": "127.0.0.1",
                "password": "password",
            },
            {
                "ipv4": "127.0.0.1",
            },
        ],
        [
            {
                "ipv4": "127.0.0.1",
                "title": "Duplicate",
            },
            {
                "ipv4": "127.0.0.2",
                "title": "Duplicate",
            },
        ],
    ],
)
def test_to_ephyr_config_json_with_duplicates(config, tmp_path):
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        f.write(json.dumps(config))
    with pytest.raises(ValueError):
        to_ephyr_config_from_input(config_path)
