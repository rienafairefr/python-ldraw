import os

import pytest

from ldraw import download, generate, LibraryImporter
from ldraw.config import Config, use
from ldraw.utils import ensure_exists


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", help="run integration tests")


def pytest_configure(config):
    download("2018-01")


def pytest_runtest_setup(item):

    run_integration = item.config.getoption("--integration")

    if run_integration and "integration" not in item.keywords:
        pytest.skip("skipping test not marked as integration")
    elif "integration" in item.keywords and not run_integration:
        pytest.skip("pass --integration option to pytest to run this test")


@pytest.fixture(scope="module")
def library_version():
    config = Config()
    LibraryImporter.set_config(config=config)
    use("2018-01")
    cached_generated = ".cached-generated"
    config.generated_path = cached_generated

    if not os.path.exists(cached_generated):
        ensure_exists(cached_generated)
        generate(config)

    yield
    LibraryImporter.clean()
