import shutil
import tempfile
import os
import mock
import pytest


@pytest.fixture
def data_dir():
    with mock.patch('appdirs.user_data_dir') as data_dir_mock:
        tmp_data_dir = tempfile.mkdtemp()
        shutil.copy(os.path.join('tmp', 'complete.zip'), tmp_data_dir)
        data_dir_mock.side_effect = lambda *args,**kwargs: tmp_data_dir
        yield data_dir_mock


def test_dynamic_colours_parts_1(data_dir):
    import ldraw
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import _Brick1X1


def test_dynamic_colours_parts_2(data_dir):
    import ldraw.library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import _Brick1X1


def test_dynamic_colours_parts_3(data_dir):
    from ldraw import library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import _Brick1X1