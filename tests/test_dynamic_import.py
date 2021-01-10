import tempfile

import os

from unittest import mock
import pytest


@pytest.fixture
def mocked_library():
    with mock.patch(
        "ldraw.get_config",
        side_effect=lambda: { "library_path": os.path.join("tests", "test_ldraw"), "generated_library_path": tempfile.mkdtemp() },
    ):
        yield
