#!/usr/bin/env python
from urllib import urlretrieve
import zipfile
import os

import shutil

from ldraw.parts import Parts

url = 'http://www.ldraw.org/library/updates/complete.zip'

retrieved = "complete.zip"

if not os.path.exists(retrieved):
    urlretrieve(url, filename=retrieved)


zip_ref = zipfile.ZipFile(retrieved, 'r')
zip_ref.extractall('tmp')
zip_ref.close()

p = Parts('tmp/ldraw/')

pass