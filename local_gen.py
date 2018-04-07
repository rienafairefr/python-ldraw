#!/usr/bin/env python
import os

from ldraw import download_main, get_data_dir
from ldraw.library_gen import library_gen_main
from appdirs import AppDirs
# useful for autocompletion in some IDEs

parts_lst = os.path.join(get_data_dir(), 'ldraw', 'parts.lst')
download_main(parts_lst)
library_gen_main(parts_lst, 'ldraw')
