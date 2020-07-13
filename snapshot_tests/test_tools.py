import shutil

import pytest
from PIL import ImageColor
from xmldiff import main, formatting

from ldraw.tools import widthxheight, vector_position
from ldraw.writers.png import PNGArgs
from ldraw.writers.svg import SVGArgs
from ldraw.tools.ldr2svg import ldr2svg
from ldraw.tools.ldr2inv import ldr2inv
from ldraw.tools.ldr2png import ldr2png
from ldraw.tools.ldr2pov import ldr2pov


INPUT_PATH = 'snapshot_tests/test_data/car.ldr'


@pytest.mark.parametrize(['func', 'suffix', 'args'], [
    (ldr2svg, '.svg',
     (vector_position('100,100,100'),
      vector_position('0,0,0'),
      SVGArgs(800, 800, background_colour=ImageColor.getrgb('#123456')))),
    (ldr2pov, '.pov',
     (vector_position('100,100,100'),
      vector_position('0,0,0'),
      '#123456')),
    (ldr2png, '.png',
     (vector_position('0,0,0'),
      vector_position('200,200,200'),
      PNGArgs(1, widthxheight('200x200'), ImageColor.getrgb('#FF0000'),
              ImageColor.getrgb('#123456')))),
    (ldr2inv, '.inv', ())
])
def test_tools(func, suffix, args, tmpdir):
    actual_path = tmpdir.join('output' + suffix)
    func(INPUT_PATH, actual_path, *args)
    actual_content = open(actual_path, 'rb').read()
    expected_file = 'snapshot_tests/test_data/car' + suffix
    expected_path = tmpdir.join('expected' + suffix)
    shutil.copy(expected_file, expected_path)
    expected_content = open(expected_file, 'rb').read()
    if suffix =='.svg':
        diff = main.diff_files(str(expected_path), str(actual_path),
                               formatter=formatting.XMLFormatter())
        pass
    assert expected_content == actual_content
