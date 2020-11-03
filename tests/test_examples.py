import contextlib
import glob
import os
import sys
import tempfile
from io import StringIO
from unittest import mock

import pytest

from ldraw import CustomImporter
from ldraw.compat import do_execfile


@pytest.fixture(scope='module')
def mocked_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_ldraw2', 'parts.lst')
    library_path = tempfile.mkdtemp()

    def get_config(): return {
        'parts.lst': parts_lst_path,
        'library': library_path,
        'others_threshold': 0
    }

    with mock.patch('ldraw.parts.get_config', side_effect=get_config):
        CustomImporter().load_module('ldraw.library')
        yield parts_lst_path

    CustomImporter.clean()


def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    import difflib
    expected = expected.splitlines(1)
    actual = actual.splitlines(1)

    diff = difflib.unified_diff(expected, actual)

    return ''.join(diff)


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


examples_dir = 'examples'
all_examples = [os.path.splitext(os.path.basename(s))[0] for s in glob.glob(os.path.join(examples_dir, '*.py'))]


def exec_example(name, save=False):
    script_file = os.path.join(examples_dir, '%s.py' % name)

    d = dict(locals(), **globals())

    with stdoutIO() as s:
        do_execfile(script_file, d, d)
    content = s.getvalue()
    expected_path = os.path.join('tests', 'test_data', 'examples', '%s.ldr' % name)
    # uncomment to save
    # open(expected_path, 'w').write(content)

    expected = open(expected_path, 'r').read()
    if expected != content:
        print(_unidiff_output(expected, content))
    assert expected == content


@pytest.mark.parametrize('example', all_examples, ids=all_examples)
def test_examples(mocked_parts_lst, example):
    exec_example(example)
