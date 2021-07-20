import contextlib
import glob
import os
import sys
import tempfile
from datetime import datetime
from io import StringIO

import pytest
from ldraw import generate, LibraryImporter

from ldraw.config import Config


@pytest.fixture(scope="module")
def test_ldraw2_config():
    generated_path = tempfile.mkdtemp(prefix=datetime.utcnow().isoformat())
    print(f'generated_path={generated_path}')
    config = Config(
        ldraw_library_path=os.path.join("tests", "test_ldraw2"),
        generated_path=generated_path
    )
    LibraryImporter.set_config(config)
    generate(config)
    yield
    LibraryImporter.clean()


def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    import difflib

    expected = expected.splitlines()
    actual = actual.splitlines()

    diff = difflib.unified_diff(expected, actual)

    return "\n".join(diff)


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


examples_dir = "examples"
all_examples = [
    os.path.splitext(os.path.basename(s))[0]
    for s in glob.glob(os.path.join(examples_dir, "*.py"))
]


def exec_example(name, save=False):
    script_file = os.path.join(examples_dir, "%s.py" % name)

    d = dict(locals(), **globals())

    with stdoutIO() as s:
        with open(script_file) as f:
            code = compile(f.read(), script_file, "exec")
        exec(code, d, d)
    content = s.getvalue()
    expected_path = os.path.join("tests", "test_data", "examples", "%s.ldr" % name)
    # uncomment to save
    # open(expected_path, 'w').write(content)

    expected = open(expected_path, "r").read()
    if expected != content:
        print(_unidiff_output(expected, content))
    assert expected == content


@pytest.mark.parametrize("example", all_examples, ids=all_examples)
def test_examples(test_ldraw2_config, example):
    exec_example(example)
