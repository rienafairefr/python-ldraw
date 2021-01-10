import os
import tempfile

import yaml
from mock import patch, mock_open
from yaml import YAMLError

from ldraw.config import get_config, write_config


def fails(*args, **kwargs):
    raise YAMLError()


@patch("yaml.load", side_effect=fails)
def test_config_cant_load(yaml_load_mock):
    yaml_load_mock.side_effect = fails

    assert get_config() == {}


@patch(
    "ldraw.config.open",
    side_effect=mock_open(read_data="ldraw_library_path: C:\\file_path"),
)
def test_config_can_load_Win(open_mock):
    assert get_config() == {"ldraw_library_path": "C:\\file_path"}


@patch(
    "ldraw.config.open",
    side_effect=mock_open(read_data="ldraw_library_path: /home/file_path"),
)
def test_config_can_load(open_mock):
    assert get_config() == {"ldraw_library_path": "/home/file_path"}


@patch("ldraw.config.get_config_file_path")
def test_write_config(config_file_path_mock):
    tmp = tempfile.mktemp()
    config_file_path_mock.side_effect = lambda: tmp
    data = {"ldraw_library_path": "/home/file_path"}
    write_config(data)

    assert yaml.load(open(tmp, "r"), Loader=yaml.SafeLoader) == data
