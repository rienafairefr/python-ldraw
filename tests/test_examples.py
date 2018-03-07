import contextlib
import glob
import os
import StringIO
import sys

import pytest
from mock import mock


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
all_examples = [os.path.splitext(os.path.basename(s))[0] for s in glob.glob(os.path.join(examples_dir, '*.py'))]


def exec_example(name, save=False):
    script_file = os.path.join(examples_dir, '%s.py'%name)

    d = dict(locals(), **globals())

    with stdoutIO() as s:
        if name == 'stairs':
            with mock.patch('sys.argv', ['', os.path.join('tmp','ldraw','parts.lst')]):
                execfile(script_file, d, d)
        else:
            execfile(script_file, d, d)
    content = s.getvalue()
    expected_path = os.path.join('tests', 'test_data', 'examples', '%s.ldr' % name)
    if save:
        open(expected_path, 'w').write(content)

    expected = open(expected_path, 'r').read()
    assert expected == content


@pytest.mark.parametrize('example', all_examples, ids=all_examples)
def test_examples(example):
    if example == 'mandelbrot':
        return
    exec_example(example)
