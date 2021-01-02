import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from datetime import timedelta
from distutils.dir_util import copy_tree
from distutils.util import strtobool
from pprint import pprint
from urllib.request import urlretrieve

import click
import inquirer
import requests
import requests_cache
from mklist.generate import generate_parts_lst

from ldraw import get_cache_dir, get_config, write_config
from ldraw.utils import ensure_exists, prompt

LDRAW_URL = 'http://www.ldraw.org/library/updates/%s'
LDRAW_PTRELEASES = 'https://www.ldraw.org/cgi-bin/ptreleases.cgi?type=ZIP'

cache_ldraw = get_cache_dir()


def get_ptreleases():
    requests_cache.install_cache(os.path.join(cache_ldraw, 'requests-cache'), expire_after=timedelta(weeks=2))

    ptreleases = ET.parse(requests.get(LDRAW_PTRELEASES).raw)
    return [
        {ch.tag: ch.text for ch in el} for el in ptreleases.findall('.//distribution')
    ]


PTRELEASES = get_ptreleases()
BASE = "2002-00"  # version 0.27
UPDATES = ["0.27"] + [el['release_id'] for el in PTRELEASES if el['release_id'] >= BASE] + ['latest']


@click.group()
def main():
    pass


def unpack_version(version_zip, output_version):
    version_dir = os.path.join(cache_ldraw, output_version)
    ensure_exists(version_dir)
    print(f'unzipping the zip {version_zip} in {version_dir}...')
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

    retrieved = os.path.join(cache_ldraw, filename)
    if not os.path.exists(retrieved):
        retrieved_, _ = urlretrieve(ldraw_url)
        shutil.copy(retrieved_, retrieved)

    return retrieved


@main.command()
def use():
    def get_choice(file):
        abs_ = os.path.join(cache_ldraw, file)
        if file == 'latest':
            release_id = str(open(os.path.join(abs_, 'release_id')).read())
            return f"latest ({release_id})"
        else:
            return file

    choices = {
        get_choice(file): file for file in os.listdir(cache_ldraw)
        if os.path.isdir(os.path.join(cache_ldraw, file)) and os.path.exists(os.path.join(cache_ldraw, file, 'targeted'))
    }
    questions = [
        inquirer.List('Ldraw library Version',
                      message="What version do you want to use?",
                      choices=choices,
                      carousel=True
                      ),
    ]
    result = inquirer.prompt(questions)
    ldraw_library_path = os.path.join(
        cache_ldraw, choices[result['Ldraw library Version']], 'ldraw'
    )

    config = get_config()
    config['ldraw_library_path'] = ldraw_library_path
    write_config(config)


@main.command()
def config():
    pprint(get_config())


@main.command()
@click.option('--version', default='latest', type=click.Choice(choices=UPDATES))
def download(version):
    """ download zip/exe, mklist, main function"""
    print('retrieve the zip from ldraw.org ...')

    release_id = version
    if version == 'latest':
        for el in PTRELEASES:
            if el['release_type'] == 'COMPLETE':
                release_id = el['release_id']
                break
    if version == 'latest' or version == "0.27":
        unpack_version(download_single_version(version), version)
    else:
        to_merge = ["0.27"] + [el['release_id'] for el in PTRELEASES if
                               el['release_id'] >= BASE and el['release_id'] < version]

        for previous_version in reversed(to_merge):
            if os.path.exists(os.path.join(cache_ldraw, previous_version)):
                copy_tree(os.path.join(cache_ldraw, previous_version), os.path.join(cache_ldraw, version))
                break

        unpack_version(download_single_version(version), version)

    version_dir = os.path.join(cache_ldraw, version)

    # copy_tree(os.path.join(version_dir, 'ldraw', 'p'), os.path.join(version_dir, 'p'))
    # copy_tree(os.path.join(version_dir, 'ldraw', 'parts'), os.path.join(version_dir, 'parts'))
    # shutil.rmtree(os.path.join(version_dir, 'ldraw'))

    version_dir = os.path.join(cache_ldraw, version)

    print('mklist...')
    generate_parts_lst(
        'description',
        os.path.join(version_dir, 'ldraw', 'parts'),
        os.path.join(version_dir, 'ldraw', 'parts.lst')
    )

    config = get_config()
    if config.get('ldraw_library_path') is None or prompt('use as the version for subsequent uses of pyLdraw ?'):
        config['ldraw_library_path'] = os.path.join(version_dir, 'ldraw')
        write_config(config)

    # marker for downloaded versions that have been explicitely targeted
    open(os.path.join(version_dir, 'targeted'), 'w').close()
    with open(os.path.join(version_dir, 'release_id'), 'w') as release_id_file:
        release_id_file.write(release_id)


if __name__ == '__main__':
    main()
