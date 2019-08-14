import os
import tempfile

import mock
import pytest

from ldraw import download


@pytest.fixture
def mocked_parts_lst(tmp_path):
    output_dir = os.path.join(str(tmp_path), 'ldraw')
    parts_lst_path = os.path.join(output_dir, 'parts.lst')
    library_path = tempfile.mkdtemp()
    download(parts_lst_path)
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path
