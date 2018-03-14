#!/usr/bin/env python
"""
Takes care of downloading the complete.zip from LDraw.org
And generating the parts.lst from it
"""
from __future__ import print_function
import shutil
import zipfile
import os

import appdirs
from mklist.generate import generate_parts_lst

from ldraw.compat import urlretrieve
from ldraw.dirs import get_data_dir
from ldraw.utils import ensure_exists


def download_main(parts_lst_path):
    """ download complete.zipn mklist, main function"""
    url = 'http://www.ldraw.org/library/updates/complete.zip'

    tmp_ldraw = ensure_exists(appdirs.user_cache_dir('pyldraw'))

    if not os.path.exists(parts_lst_path):
        retrieved = os.path.join(tmp_ldraw, "complete.zip")

        if not os.path.exists(retrieved):
            print('retrieve the complete.zip from ldraw.org ...')
            urlretrieve(url, filename=retrieved)

        ldraw_path = os.path.join(tmp_ldraw, 'ldraw')
        if not os.path.exists(ldraw_path):
            print('unzipping the complete.zip ...')
            zip_ref = zipfile.ZipFile(retrieved, 'r')
            zip_ref.extractall(tmp_ldraw)
            zip_ref.close()

        output_dir = ensure_exists(os.path.abspath(os.path.join(parts_lst_path, '..')))

        shutil.move(os.path.join(tmp_ldraw, 'ldraw', 'parts'), output_dir)
        shutil.move(os.path.join(tmp_ldraw, 'ldraw', 'p'), output_dir)
        shutil.move(os.path.join(tmp_ldraw, 'ldraw', 'LDConfig.ldr'), output_dir)

        if not os.path.exists(parts_lst_path):
            print('mklist...')
            generate_parts_lst('description',
                               os.path.join(output_dir, 'parts'),
                               parts_lst_path)


if __name__ == '__main__':
    download_main(os.path.join(get_data_dir(), 'ldraw', 'parts.lst'))
