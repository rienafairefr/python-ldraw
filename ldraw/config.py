"""
takes care of reading and writing a configuration in config.yml
"""
import os
from os.path import join

import sys
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
        return config
    except (OSError, yaml.YAMLError, IOError, EnvironmentError) as e:
        parts_lst_path = os.environ.get('LDRAW_PARTS_LST')
        if parts_lst_path:
            return {
                'parts.lst': parts_lst_path
            }
        else:
            return {
                'parts.lst': join(data_dir, 'ldraw', 'parts.lst')
            }


def write_config(config_dict):
    """ write the config to config.yml """
    yaml.dump(config_dict, open(get_config_file_path(), 'w'))


if __name__ == '__main__':
    print('Configuration file path:')
    print(get_config_file_path())
    print('Configuration used:')
    yaml.dump(get_config(), sys.stdout, default_flow_style=False)