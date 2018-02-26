import tempfile

from ldraw.tools.ldr2inv import ldr2inv
from ldraw.tools.ldr2png import ldr2png
from ldraw.tools.ldr2pov import ldr2pov
from ldraw.tools.ldr2svg import ldr2svg

PARTS_PATH = 'tmp/ldraw/parts.lst'
INPUT_PATH = 'tests/test_data/car.ldr'


def tool_test(func, suffix):
    fd, file = tempfile.mkstemp(suffix=suffix)
    func(file)
    content = open(file,'r').read()
    expected = open('tests/test_data/car' + suffix).read()
    assert expected == content


def test_ldr2inv():
    tool_test(lambda f: ldr2inv(PARTS_PATH, INPUT_PATH, f), '.inv')


def test_ldr2png():
    tool_test(lambda f: ldr2png(PARTS_PATH, INPUT_PATH, f,
            50, '800x800', '100,100,100', '0,0,0',
            '#123456', '#FF0000'),'.png')


def test_ldr2pov():
    tool_test(lambda f: ldr2pov(PARTS_PATH, INPUT_PATH, f,
            '100,100,100', '0,0,0',
            '#123456'), '.pov')


def test_ldr2svg():
    tool_test(lambda f: ldr2svg(PARTS_PATH, INPUT_PATH, f,
            '800x800','100,100,100', '0,0,0',
            '#123456'), '.svg')
