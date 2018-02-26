import shutil
import tempfile

from PIL import ImageColor

from ldraw.tools import widthxheight, vector_position
from ldraw.writers.png import PNGArgs
from ldraw.writers.svg import SVGArgs

from tests.utils import mocked_parts_lst

INPUT_PATH = 'tests/test_data/car.ldr'


def tool_test(func, suffix):
    fd, file = tempfile.mkstemp(prefix='pyldraw-', suffix=suffix)
    fde, filee = tempfile.mkstemp(prefix='pyldraw-', suffix=suffix)
    func(file)
    content = open(file, 'rb').read()
    # uncomment to save content to expected
    open('tests/test_data/car' + suffix, 'wb').write(content)

    expected_file = 'tests/test_data/car' + suffix
    shutil.copy(expected_file, filee)
    expected = open(expected_file, 'rb').read()
    assert expected == content


def test_ldr2inv(mocked_parts_lst):
    from ldraw.tools.ldr2inv import ldr2inv
    tool_test(lambda f: ldr2inv(INPUT_PATH, f), '.inv')


def test_ldr2png(mocked_parts_lst):
    from ldraw.tools.ldr2png import ldr2png
    tool_test(lambda f: ldr2png(INPUT_PATH, f,
                                vector_position('0,0,0'),
                                vector_position('200,200,200'),
                                PNGArgs(1, widthxheight('200x200'), ImageColor.getrgb('#FF0000'), ImageColor.getrgb('#123456'))),
              '.png')


def test_ldr2pov(mocked_parts_lst):
    from ldraw.tools.ldr2pov import ldr2pov
    tool_test(lambda f: ldr2pov(INPUT_PATH, f,
                                vector_position('100,100,100'),
                                vector_position('0,0,0'),
                                '#123456'),
              '.pov')


def test_ldr2svg(mocked_parts_lst):
    from ldraw.tools.ldr2svg import ldr2svg
    tool_test(lambda f: ldr2svg(INPUT_PATH, f,
                                vector_position('100,100,100'),
                                vector_position('0,0,0'),
                                SVGArgs(800, 800, background_colour=ImageColor.getrgb('#123456'))),
              '.svg')
