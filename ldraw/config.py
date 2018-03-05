import appdirs
import os
from os.path import exists, join

import yaml

from ldraw.dirs import get_config_dir, get_data_dir

config_dir = get_config_dir()
data_dir = get_data_dir()

config_file_path = join(config_dir, 'config.yml')


def get_config():
    try:
        config = yaml.load(open(config_file_path, 'r'))
        parts_path = os.environ.get('LDRAW_PARTS')
        if parts_path:
            config['parts'] = parts_path
        parts_lst_path = os.environ.get('LDRAW_PARTS_LST')
        if parts_lst_path:
            config['parts.lst'] = parts_lst_path
        return config
    except:
        ldraw = join(data_dir, 'ldraw')
        conf = {
            'parts': join(ldraw, 'parts'),
            'parts.lst': join(ldraw, 'parts.lst')
        }
        write_config(conf)
        return conf


def write_config(config_dict):
    yaml.dump(config_dict, open(config_file_path, 'w'))