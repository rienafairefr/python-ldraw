import tempfile

import os

from os.path import join

import pytest
import sys

from ldraw.colour import Colour
from ldraw.library_gen import library_gen_main


@pytest.fixture
def data_dir():
    yield tempfile.mkdtemp()


def test_library_gen_files(data_dir):
    """ generated library contains the right files """
    library_gen_main('tests/test_ldraw/parts.lst', data_dir)

    content = {os.path.relpath(os.path.join(dp, f), data_dir) for dp, dn, fn in os.walk(data_dir) for f in fn}

    library = {'__init__.py',
               'colours.py',
               'license.txt',
               join('parts', '__init__.py'),
               join('parts', 'others.py')}

    assert content == {join('library', el) for el in library}


# noinspection PyUnresolvedReferences, PyPackageRequirements
def test_library_gen_import(data_dir):
    """ generated library is importable """
    library_gen_main('tests/test_ldraw/parts.lst', data_dir)

    sys.path.append(data_dir)

    import library

    assert library.__all__ == ['colours']

    from library.parts import *

    assert library.parts.__all__ == ['others']

    from library.parts.others import *

    assert Brick2X4 == "3001"

    from library.colours import *

    expected_color = Colour(189, "Reddish_Gold", "#AC8247", 255, ['PEARLESCENT'])

    assert ColoursByCode == {expected_color.code:expected_color}
    assert ColoursByName == {expected_color.name:expected_color}

    assert Reddish_Gold == expected_color
