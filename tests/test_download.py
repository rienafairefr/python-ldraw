import tempfile
import zipfile

from mock import call, patch, Mock
import os
import pytest
from ldraw.download import download_main, LDRAW_URL


@pytest.fixture
def output_dir():
    return tempfile.mkdtemp()


def exists_needs_retrieve(s):
    if os.path.basename(s) == 'complete.zip':
        return False
    return True


def exists_needs_unzip(s):
    if os.path.basename(s) == 'complete.zip':
        return True
    if os.path.basename(s) == 'ldraw':
        return False
    return True


@patch('ldraw.download.urlretrieve')
@patch('os.path.exists', side_effect=exists_needs_retrieve)
def test_download_needs_retrieve(os_path_exists_mock, urlretrieve_mock, output_dir):
    download_main(output_dir)

    urlretrieve_mock.assert_called_once_with(LDRAW_URL,
                                                    filename=os.path.join(output_dir, 'complete.zip'))


@patch('ldraw.download.urlretrieve')
@patch('os.path.exists', side_effect=exists_needs_unzip)
@patch('zipfile.ZipFile', spec=zipfile.ZipFile)
def test_download_needs_unzip(zip_mock, os_path_exists_mock, urlretrieve_mock, output_dir):
    archive = Mock()
    mocked_extract = Mock()
    archive.return_value.extractall = mocked_extract
    zip_mock.return_value.__enter__ = archive

    download_main(output_dir)

    assert not urlretrieve_mock.called

    assert zip_mock.called

    mocked_extract.assert_called_once_with(output_dir)


def exists_needs_mklist(s):
    if os.path.basename(s) == 'complete.zip':
        return True
    if os.path.basename(s) == 'ldraw':
        return True
    return False


@patch('os.path.exists', side_effect=exists_needs_mklist)
@patch('ldraw.download.generate_parts_lst')
def test_download_needs_mklist(exists_mock, mklist_mock, output_dir):
    download_main(output_dir)

    mklist_mock.assert_any_call(os.path.join(output_dir, 'ldraw', 'p.lst'))
    mklist_mock.assert_any_call(os.path.join(output_dir, 'ldraw', 'parts.lst'))
