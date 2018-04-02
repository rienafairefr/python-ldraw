import os
import tempfile

import yaml
from mock import patch
from yaml import YAMLError

from ldraw.config import get_config, write_config
from ldraw.dirs import get_data_dir


def fails(*args, **kwargs):
    raise YAMLError()


@patch('yaml.load', side_effect=fails)
@patch.dict(os.environ, {'LDRAW_PARTS_LST': '12345'})
def test_config_env_parts_lst(yaml_load_mock):
    assert get_config()['parts.lst'] == '12345'


@patch('yaml.load', side_effect=fails)
def test_config_cant_load(yaml_load_mock):
    yaml_load_mock.side_effect = fails
    expected = os.path.join(get_data_dir(), 'ldraw', 'parts.lst')

    assert get_config()['parts.lst'] == expected


@patch('yaml.load', side_effect=lambda o: {'parts.lst': '54321'})
def test_config_can_load(yaml_load_mock):
    assert get_config() == {'parts.lst': '54321'}


@patch('ldraw.config.get_config_file_path')
def test_write_config(config_file_path_mock):
    tmp = tempfile.mktemp()
    config_file_path_mock.side_effect = lambda: tmp
    data = {'parts.lst':'2468'}
    write_config(data)

    assert yaml.load(open(tmp, 'r')) == data