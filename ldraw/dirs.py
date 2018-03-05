import appdirs
import os


def get_(fun):
    def wrapped():
        _dir = fun('pyldraw')
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return _dir
    return wrapped


if os.environ.get('LDRAW_DATA_DIR'):
    get_data_dir = get_(lambda s: os.environ.get('LDRAW_DATA_DIR'))
else:
    get_data_dir = get_(appdirs.user_data_dir)
get_config_dir = get_(appdirs.user_config_dir)

