import codecs
import difflib
import shutil
import tempfile

import pytest
from PIL import ImageColor

# ! no ldraw.* imports up here


INPUT_PATH = "tests/test_data/car.ldr"


def tool_test(func, suffix):
    fd, file = tempfile.mkstemp(prefix="pyldraw-result-", suffix=suffix)
    fde, tmp_expected_file = tempfile.mkstemp(prefix="pyldraw-expected-", suffix=suffix)
    func(file)
    content = open(file, "rb").read()
    # uncomment to save content to expected
    # open('tests/test_data/car' + suffix, 'wb').write(content)

    expected_file = "tests/test_data/car" + suffix
    shutil.copy(expected_file, tmp_expected_file)
    expected = open(expected_file, "rb").read()
    if expected != content:
        pass
    assert expected == content


def test_ldr2inv(library_version):
    from ldraw.tools.ldr2inv import ldr2inv

    tool_test(lambda f: ldr2inv(
        library_version,
        codecs.open(INPUT_PATH, 'r', encoding='utf-8'), f),
        ".inv",
        )


def test_ldr2png(library_version):
    from ldraw.tools.ldr2png import ldr2png
    from ldraw.tools import widthxheight, vector_position
    from ldraw.writers.png import PNGArgs

    tool_test(
        lambda f: ldr2png(
            library_version,
            codecs.open(INPUT_PATH, 'r', encoding='utf-8'),
            f,
            vector_position("0,0,0"),
            vector_position("200,200,200"),
            PNGArgs(
                1,
                widthxheight("800x800"),
                ImageColor.getrgb("#FF0000"),
                ImageColor.getrgb("#123456"),
            ),
        ),
        ".png",
    )


def test_ldr2pov(library_version):
    from ldraw.tools.ldr2pov import ldr2pov
    from ldraw.tools import vector_position

    tool_test(
        lambda f: ldr2pov(
            library_version,
            codecs.open(INPUT_PATH, 'r', encoding='utf-8'),
            f,
            vector_position("200,-200,200"),
            vector_position("0,0,0"),
            "#123456",
        ),
        ".pov",
    )


def test_ldr2svg(library_version):
    from ldraw.tools.ldr2svg import ldr2svg
    from ldraw.tools import vector_position
    from ldraw.writers.svg import SVGArgs

    tool_test(
        lambda f: ldr2svg(
            library_version,
            codecs.open(INPUT_PATH, 'r', encoding='utf-8'),
            f,
            vector_position("200,200,200"),
            vector_position("0,0,0"),
            SVGArgs(800, 800, background_colour=ImageColor.getrgb("#123456")),
        ),
        ".svg",
    )
