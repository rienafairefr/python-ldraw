""" data and config directories """

import appdirs

from ldraw.utils import ensure_exists

PYLDRAW = "pyldraw"


def get_data_dir():
    """ get the directory where to put some data """
    return ensure_exists(appdirs.user_data_dir(PYLDRAW))


def get_config_dir():
    """ get the directory where the config is """
    return ensure_exists(appdirs.user_config_dir(PYLDRAW))


def get_cache_dir():
    return ensure_exists(appdirs.user_cache_dir(PYLDRAW))
