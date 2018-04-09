import tempfile

import os

import mock
import pytest

from ldraw import download_main, CustomImporter
from ldraw.colour import Colour


@pytest.fixture
def mocked_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_ldraw', 'parts.lst')
    library_path = tempfile.mkdtemp()
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path


def test_dynamic_import(mocked_parts_lst):
    from ldraw.library.colours import Reddish_Gold
    from ldraw.library.parts.others import Brick2X4
    assert Reddish_Gold == Colour(189, "Reddish_Gold", "#AC8247", 255, ['PEARLESCENT'])
    assert Brick2X4 == "3001"

    CustomImporter.clean()