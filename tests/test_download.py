import tempfile
import zipfile

import appdirs
from mock import *
import os
import pytest
from ldraw.download import download_main, LDRAW_URL


@pytest.fixture
def output_dir():
    return tempfile.mkdtemp()


@patch('ldraw.download.urlretrieve')
@patch('os.path.exists', side_effect=lambda s:False)
@patch('zipfile.ZipFile', spec=zipfile.ZipFile)
@patch('ldraw.download.generate_parts_lst')
@patch('ldraw.download.copy_tree')
def test_download(copy_tree_mock, mklist_mock, zip_mock, os_path_exists_mock, urlretrieve_mock, output_dir):
    tmp_ldraw = appdirs.user_cache_dir('pyldraw')
    parts_lst_path = os.path.join(output_dir, 'parts.lst')
    output_2 = os.path.join(output_dir, 'parts')
    download_main(parts_lst_path)

    urlretrieve_mock.assert_called_once_with(LDRAW_URL,
                                             filename=os.path.join(tmp_ldraw, 'complete.zip'))

    zip_mock.assert_called_once_with(os.path.join(tmp_ldraw, 'complete.zip'), 'r')

    copy_tree_mock.assert_called_once_with(os.path.join(tmp_ldraw,'ldraw'), output_dir)

    mklist_mock.assert_called_once_with('description', output_2, parts_lst_path)



