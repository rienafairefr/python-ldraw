import pytest
from click.testing import CliRunner

from ldraw.__main__ import download, UPDATES


@pytest.mark.integration
def test_download():
    runner = CliRunner()
    for update in UPDATES:
        result = runner.invoke(download, ['--version', update])
        assert result.exit_code == 0
