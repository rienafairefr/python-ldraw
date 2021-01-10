import os
from os.path import join

import tempfile
from unittest import mock
import pytest

from ldraw.generation.generation import do_generate
from ldraw.colour import Colour


@pytest.fixture
def mocked_library_path():
    ldraw_library_output_path = tempfile.mkdtemp()
    do_generate(ldraw_library_output_path)
    with mock.patch(
        "ldraw.get_config",
        side_effect=lambda: {"ldraw_library_path": ldraw_library_output_path},
    ):
        yield ldraw_library_output_path


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


def test_library_gen_import(mocked_library_path):
    """ generated library is importable """
    from ldraw import library
    import ldraw.library

    assert library.__all__ == ["colours"]

    assert library.parts.__all__ == ["Brick2X4"]

    from ldraw.library.parts import Brick2X4

    assert Brick2X4 == "3001"

    from ldraw.library.colours import Reddish_Gold, ColoursByName, ColoursByCode

    expected_color = Colour(189, "Reddish_Gold", "#AC8247", 255, ["PEARLESCENT"])

    assert ColoursByCode == {expected_color.code: expected_color}
    assert ColoursByName == {expected_color.name: expected_color}

    assert Reddish_Gold == expected_color
