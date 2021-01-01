import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from datetime import timedelta
from distutils.dir_util import copy_tree
from urllib.request import urlretrieve

import click
import requests
import requests_cache
from mklist.generate import generate_parts_lst

from ldraw import get_cache_dir
from ldraw.utils import ensure_exists

LDRAW_URL = 'http://www.ldraw.org/library/updates/%s'
LDRAW_PTRELEASES = 'https://www.ldraw.org/cgi-bin/ptreleases.cgi?type=ZIP'

tmp_ldraw = get_cache_dir()


def get_ptreleases():
    requests_cache.install_cache(os.path.join(tmp_ldraw, 'requests-cache'), expire_after=timedelta(weeks=2))

    ptreleases = ET.parse(requests.get(LDRAW_PTRELEASES).raw)
    return [
        {ch.tag: ch.text for ch in el} for el in ptreleases.findall('//distribution')
    ]

PTRELEASES = get_ptreleases()
BASE = "2002-00"  # version 0.27
UPDATES = ["0.27"] + [el['release_id'] for el in PTRELEASES if el['release_id'] >= BASE] + ['latest']


@click.group()
def main():
    pass


def unpack_version(version_zip, output_version):
    version_dir = os.path.join(tmp_ldraw, output_version)
    ensure_exists(version_dir)
    print(f'unzipping the zip {version_zip}...')
    zip_ref = zipfile.ZipFile(version_zip, 'r')
    zip_ref.extractall(version_dir)
    zip_ref.close()


def download_single_version(version):
    if version == 'latest':
        filename = 'complete.zip'
    elif version == "0.27":
        filename = "ldraw027.zip"
    else:
        short_version = version[2:4] + version[5:]
        filename = f"lcad{short_version}.zip"

    ldraw_url = LDRAW_URL % filename

    retrieved = os.path.join(tmp_ldraw, filename)
    if not os.path.exists(retrieved):
        urlretrieve(ldraw_url, filename=retrieved)

    return retrieved


@main.command()
@click.option('--version', default='latest', type=click.Choice(choices=UPDATES))
def download(version):
    """ download zip/exe, mklist, main function"""
    print('retrieve the zip from ldraw.org ...')

    if version == 'latest' or version == "0.27":
        unpack_version(download_single_version(version), version)
    else:
        to_download = ["0.27"] + [el['release_id'] for el in PTRELEASES if
                                  el['release_id'] >= BASE and el['release_id'] <= version]

        for previous_version in to_download:
            unpack_version(download_single_version(previous_version), version)

    version_dir = os.path.join(tmp_ldraw, version)

    copy_tree(os.path.join(version_dir, 'ldraw', 'p'), os.path.join(version_dir, 'p'))
    copy_tree(os.path.join(version_dir, 'ldraw', 'parts'), os.path.join(version_dir, 'parts'))
    shutil.rmtree(os.path.join(version_dir, 'ldraw'))

    version_dir = os.path.join(tmp_ldraw, version)
    parts_lst_path = os.path.join(version_dir, 'parts.lst')

    print('mklist...')
    generate_parts_lst('description',
                       os.path.join(version_dir, 'parts'),
                       parts_lst_path)


if __name__ == '__main__':
    main()
