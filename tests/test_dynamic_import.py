import os
import tempfile
from datetime import datetime

import pytest

from ldraw import LibraryImporter
from ldraw.config import Config


@pytest.fixture
def mocked_library():
    generated_path = tempfile.mkdtemp(prefix=datetime.utcnow().isoformat())
    print(f'{generated_path=}')
    config = Config(
        ldraw_library_path=os.path.join("tests", "test_ldraw"),
        generated_path=generated_path
    )
    LibraryImporter.set_config(config)
    yield
    LibraryImporter.clean()
