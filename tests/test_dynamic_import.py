import tempfile

import os

import mock
import pytest

from ldraw import download_main
from ldraw.colour import Colour


@pytest.fixture
def mocked_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_ldraw', 'parts.lst')
    library_path = tempfile.mkdtemp()
    download_main(parts_lst_path)
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path


def test_dynamic_colours_parts_1(mocked_parts_lst):
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1
    assert Black == Colour(0, "Black", "#05131D", 255, [])
    assert Brick1X1 == "3005"



def test_dynamic_colours_parts_2(mocked_parts_lst):
    import ldraw.library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1
    assert Black == Colour(0, "Black", "#05131D", 255, [])
    assert Brick1X1 == "3005"


def test_dynamic_colours_parts_3(mocked_parts_lst):
    from ldraw import library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1
    assert Black == Colour(0, "Black", "#05131D", 255, [])
    assert Brick1X1 == "3005"