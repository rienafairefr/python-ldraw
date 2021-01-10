import os

import pytest


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", help="run integration tests")


def pytest_runtest_setup(item):

    run_integration = item.config.getoption("--integration")

    if run_integration and "integration" not in item.keywords:
        pytest.skip("skipping test not marked as integration")
    elif "integration" in item.keywords and not run_integration:
        pytest.skip("pass --integration option to pytest to run this test")


@pytest.fixture
def mocked_library(tmp_path):
    output_dir = os.path.join(str(tmp_path), "ldraw")
    download(parts_lst_path)
    with mock.patch(
        "ldraw.get_config",
        side_effect=lambda: {"parts.lst": parts_lst_path, "library": library_path},
    ):
        yield parts_lst_path