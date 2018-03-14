"""
takes care of reading and writing a configuration in config.yml
"""
import os
from os.path import join
import yaml

from ldraw.dirs import get_config_dir, get_data_dir


def get_config_file_path():
    """ get the config file path """
    return join(get_config_dir(), 'config.yml')


def get_config():
    """ get the configuration from config.yml, create it if not there """
    data_dir = get_data_dir()
    try:
        config = yaml.load(open(get_config_file_path(), 'r'))
        parts_path = os.environ.get('LDRAW_PARTS')
        if parts_path:
            config['parts'] = parts_path
        parts_lst_path = os.environ.get('LDRAW_PARTS_LST')
        if parts_lst_path:
            config['parts.lst'] = parts_lst_path
        return config
    except (OSError, yaml.YAMLError, IOError, EnvironmentError):
        ldraw = join(data_dir, 'ldraw')
        conf = {
            'parts': join(ldraw, 'parts'),
            'parts.lst': join(ldraw, 'parts.lst')
        }
        write_config(conf)
        return conf


def write_config(config_dict):
    """ write the config to config.yml """
    yaml.dump(config_dict, open(get_config_file_path(), 'w'))
