import glob
import logging
import os
import shutil
import zipfile
from datetime import timedelta
from urllib.request import urlretrieve
from xml.etree import ElementTree as ET

import requests
import requests_cache
from mklist.generate import generate_parts_lst

from ldraw.dirs import get_cache_dir
from ldraw.utils import path_insensitive

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://github.com/rienafairefr/ldraw-parts/archive/%s.zip"
LDRAW_PTRELEASES = "https://www.ldraw.org/cgi-bin/ptreleases.cgi?type=ZIP"
cache_ldraw = get_cache_dir()


def get_ptreleases():
    requests_cache.install_cache(
        os.path.join(cache_ldraw, "requests-cache"), expire_after=timedelta(weeks=2)
    )

    ptreleases = ET.parse(requests.get(LDRAW_PTRELEASES).raw)
    return [
        {ch.tag: ch.text for ch in el} for el in ptreleases.findall(".//distribution")
    ]


PTRELEASES = get_ptreleases()
BASE = "2002-00"  # version 0.27
UPDATES = (
    ["0.27"]
    + [el["release_id"] for el in PTRELEASES if el["release_id"] >= BASE]
    + ["latest"]
)


def unpack_version(version_zip, version):
    print(f"unzipping the zip {version_zip}...")
    zip_ref = zipfile.ZipFile(version_zip, "r")
    zip_ref.extractall(cache_ldraw)
    zip_ref.close()
    shutil.move(
        os.path.join(cache_ldraw, f"ldraw-parts-{version}"),
        os.path.join(cache_ldraw, version)
    )


def download_version(version):
    filename = f"{version}.zip"

    archive_url = ARCHIVE_URL % version

    retrieved = os.path.join(cache_ldraw, filename)
    if not os.path.exists(retrieved):
        retrieved_, _ = urlretrieve(archive_url)
        shutil.copy(retrieved_, retrieved)

    return retrieved


def download(version):
    release_id = version
    if version == "latest":
        for el in PTRELEASES:
            if el["release_type"] == "COMPLETE":
                release_id = el["release_id"]
                break

    if os.path.exists(os.path.join(cache_ldraw, version)):
        print(f'{version} already downloaded')
        return
    unpack_version(download_version(version), version)

    # copy_tree(os.path.join(version_dir, 'ldraw', 'p'), os.path.join(version_dir, 'p'))
    # copy_tree(os.path.join(version_dir, 'ldraw', 'parts'), os.path.join(version_dir, 'parts'))
    # shutil.rmtree(os.path.join(version_dir, 'ldraw'))

    version_dir = os.path.join(cache_ldraw, version)

    print(glob.glob(os.path.join(version_dir, '*')))
    print(glob.glob(version_dir))

    print("mklist...")
    generate_parts_lst(
        "description",
        path_insensitive(os.path.join(version_dir, "ldraw", "parts")),
        path_insensitive(os.path.join(version_dir, "ldraw", "parts.lst")),
    )
    with open(os.path.join(version_dir, "release_id"), "w") as release_id_file:
        release_id_file.write(release_id)
