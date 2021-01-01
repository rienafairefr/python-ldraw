import tempfile

import os

from unittest import mock
import pytest


@pytest.fixture
def mocked_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_ldraw', 'parts.lst')
    library_path = tempfile.mkdtemp()
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path
