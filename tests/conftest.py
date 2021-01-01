import pytest


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", help="run integration tests")


def pytest_runtest_setup(item):

    run_integration = item.config.getoption("--integration")

    if run_integration and 'integration' not in item.keywords:
        pytest.skip("skipping test not marked as integration")
    elif 'integration' in item.keywords and not run_integration:
        pytest.skip("pass --integration option to pytest to run this test")