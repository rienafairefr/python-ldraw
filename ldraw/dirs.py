""" data and config directories """

import os
import appdirs

from ldraw.utils import ensure_exists


def get_data_dir():
    """ get the directory where to put some data """
    return ensure_exists(
        os.environ.get('LDRAW_DATA_DIR', appdirs.user_data_dir('pyldraw')))


def get_config_dir():
    """ get the directory where the config is """
    return ensure_exists(appdirs.user_config_dir('pyldraw'))
