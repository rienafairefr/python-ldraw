import os
import zipfile

import appdirs
from mock import *

from ldraw import download, LDRAW_URL


@patch('os.path.exists', side_effect=lambda s: False)
@patch('zipfile.ZipFile', spec=zipfile.ZipFile)
@patch('ldraw.urlretrieve')
@patch('ldraw.generate_parts_lst')
@patch('ldraw.copy_tree')
def test_download(copy_tree_mock, generate_parts_lst_mock, urlretrieve_mock,
                  zip_mock, os_path_exists_mock, tmp_path):
    output_dir = str(tmp_path)
    tmp_ldraw = appdirs.user_cache_dir('pyldraw')
    parts_lst_path = os.path.join(output_dir, 'parts.lst')
    output_2 = os.path.join(output_dir, 'parts')
    download(output_dir)

    urlretrieve_mock.assert_called_once_with(LDRAW_URL,
                                             filename=os.path.join(tmp_ldraw, 'complete.zip'))

    zip_mock.assert_called_once_with(os.path.join(tmp_ldraw, 'complete.zip'), 'r')

    copy_tree_mock.assert_called_once_with(os.path.join(tmp_ldraw,'ldraw'), output_dir)

    generate_parts_lst_mock.assert_called_once_with('description', output_2, parts_lst_path)



