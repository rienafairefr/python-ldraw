#!/usr/bin/env python
import os

os.environ['LDRAW_DATA_DIR'] = 'ldraw'

from ldraw.generate import generate_main
# useful for autocompletion in some IDEs

generate_main('ldraw')
