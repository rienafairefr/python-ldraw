import os
import mock

from ldraw import download_main

parts_lst_path = os.path.join('tmp', 'ldraw', 'parts.lst')
download_main(parts_lst_path)


def mocked_parts_lst():
    return {'parts.lst': parts_lst_path}


def with_mocked_parts_lst(fun):
    def wrapped(*args, **kwargs):
        with mock.patch('ldraw.get_config', side_effect=mocked_parts_lst):
            return fun(*args, **kwargs)
    return wrapped