import os
import tempfile

import mock
import pytest

from ldraw import CustomImporter, try_download_generate_lib


@pytest.fixture(scope='module')
def snapshot_parts_lst():
    parts_lst_path = os.path.join('tests', 'test_snapshot_ldraw', 'parts.lst')
    library_path = tempfile.mkdtemp()

    def get_config():
        return {
            'parts.lst': parts_lst_path,
            'library': library_path,
            'others_threshold': 0
        }

    CustomImporter.clean()
    with mock.patch('ldraw.get_config', side_effect=get_config):
        with mock.patch('ldraw.tools.get_config', side_effect=get_config):
            with mock.patch('ldraw.config.get_config', side_effect=get_config):
                try_download_generate_lib()
                yield parts_lst_path

    CustomImporter.clean()
