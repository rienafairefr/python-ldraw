import os
import tempfile

import pytest

from ldraw.config import Config


@pytest.fixture
def mocked_library():
    config = Config.get()
    config.ldraw_library_path = os.path.join("tests", "test_ldraw")
    config.generated_path = tempfile.mkdtemp()

    yield
    Config.reset()
    LibraryImporter.clean()
