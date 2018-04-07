#!/usr/bin/env python
"""
Takes care of downloading the complete.zip from LDraw.org
And generating the parts.lst from it
"""
from __future__ import print_function
import zipfile
import os
from distutils.dir_util import copy_tree

import appdirs
from mklist.generate import generate_parts_lst

from ldraw.compat import urlretrieve
from ldraw.dirs import get_data_dir
from ldraw.utils import ensure_exists

LDRAW_URL = 'http://www.ldraw.org/library/updates/complete.zip'


def download_main(parts_lst_path):
    """ download complete.zip, mklist, main function"""
    tmp_ldraw = ensure_exists(appdirs.user_cache_dir('pyldraw'))

    if not os.path.exists(parts_lst_path):
        retrieved = os.path.join(tmp_ldraw, "complete.zip")

        print('retrieve the complete.zip from ldraw.org ...')
        urlretrieve(LDRAW_URL, filename=retrieved)

        print('unzipping the complete.zip ...')
        zip_ref = zipfile.ZipFile(retrieved, 'r')
        zip_ref.extractall(tmp_ldraw)
        zip_ref.close()

        output_dir = ensure_exists(os.path.abspath(os.path.join(parts_lst_path, '..')))

        copy_tree(os.path.join(tmp_ldraw, 'ldraw'), os.path.join(output_dir))

        print('mklist...')
        generate_parts_lst('description',
                           os.path.join(output_dir, 'parts'),
                           parts_lst_path)


if __name__ == '__main__':
    download_main(os.path.join(get_data_dir(), 'ldraw', 'parts.lst'))
