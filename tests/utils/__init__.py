import os
import tempfile

import mock
import pytest

from ldraw import download_main


@pytest.fixture
def mocked_parts_lst():
    parts_lst_path = os.path.join('tmp', 'ldraw', 'parts.lst')
    library_path = tempfile.mkdtemp()
    download_main(parts_lst_path)
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path
