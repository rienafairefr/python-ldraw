#!/usr/bin/env python
import os

from ldraw.dirs import get_data_dir
from ldraw import generate, download

# useful for autocompletion in some IDEs

output_dir = os.path.join(get_data_dir(), 'ldraw')
parts_lst = os.path.join(output_dir, 'parts.lst')
if not os.path.exists(output_dir):
    download(output_dir)
generate(parts_lst, 'ldraw', force=True)
