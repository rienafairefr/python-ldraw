import contextlib
import glob
import os
import sys
import tempfile

import mock
import pytest

from ldraw import CustomImporter
from ldraw.compat import StringIO, do_execfile, PY2


@pytest.fixture(scope='module')
def mocked_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_ldraw2', 'parts.lst')
    library_path = tempfile.mkdtemp()
    with mock.patch('ldraw.get_config', side_effect=lambda: {'parts.lst': parts_lst_path, 'library': library_path}):
        yield parts_lst_path

    CustomImporter.clean()


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

    import ldraw.library
    with stdoutIO() as s:
        do_execfile(script_file, d, d)
    content = s.getvalue()
    expected_path = os.path.join('tests', 'test_data', 'examples', '%s.ldr' % name)
    expected_path_py3 = os.path.join('tests', 'test_data', 'examples', '%s.py3.ldr' % name)
    if not PY2 and os.path.exists(expected_path_py3):
        expected_path = expected_path_py3
    # uncomment to save
    # open(expected_path, 'w').write(content)

    expected = open(expected_path, 'r').read()
    assert expected == content


@pytest.mark.parametrize('example', all_examples, ids=all_examples)
def test_examples(mocked_parts_lst, example):
    exec_example(example)
