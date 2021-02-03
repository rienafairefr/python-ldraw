import os
import tempfile
from os.path import join

import pytest

from ldraw import generate, LibraryImporter
from ldraw.colour import Colour
from ldraw.config import Config


@pytest.fixture
def test_ldraw_library():
    config = Config.get()
    config.generated_path = tempfile.mkdtemp()
    config.ldraw_library_path = os.path.join("tests", "test_ldraw")
    generate(config, warn=False)
    yield
    Config.reset()
    LibraryImporter.clean()


def test_library_gen_files(mocked_library_path):
    """ generated library contains the right files """
    content = {
        os.path.relpath(os.path.join(dp, f), mocked_library_path)
        for dp, dn, fn in os.walk(mocked_library_path)
        for f in fn
    }

    library = {
        "__init__.py",
        "colours.py",
        "license.txt",
        "__hash__",
        join("parts", "__init__.py"),
        join("parts", "others.py"),
    }

    assert content == {join("library", el) for el in library}


def test_library_gen_import(test_ldraw_library):
    """ generated library is importable """
    from ldraw import library

    assert set(library.__all__) == {'parts', 'colours'}

    assert dir(library.parts).__all__ == ["Brick2X4"]

    from ldraw.library.parts import Brick2X4

    assert Brick2X4 == "3001"

    from ldraw.library.parts.bricks import Brick2X4

    assert Brick2X4 == "3001"

    from ldraw.library.colours import Reddish_Gold, ColoursByName, ColoursByCode

    expected_color = Colour(189, "Reddish_Gold", "#AC8247", 255, ["PEARLESCENT"])

    assert ColoursByCode == {expected_color.code: expected_color}
    assert ColoursByName == {expected_color.name: expected_color}

    assert Reddish_Gold == expected_color
