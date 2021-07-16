import logging
import os
from pprint import pprint

import click
import yaml

from ldraw.config import select_library_version, use as do_use, Config
from ldraw.dirs import get_data_dir, get_cache_dir
from ldraw.downloads import download as do_download, UPDATES
from ldraw.generation.exceptions import UnwritableOutput
from ldraw import generate as do_generate, LibraryImporter
from ldraw.utils import prompt


@click.group()
@click.option("--debug", is_flag=True)
def main(debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@main.command()
@click.option("--version", type=click.Choice(choices=UPDATES))
def use(version):
    return do_use(version)


@main.command()
@click.option(
    "--force",
    help="re-generate even if it's apparently not needed",
    required=False,
    is_flag=True,
)
@click.option(
    "--destination",
    help="generate in another dir. 'library' folder will be created below that. If not specified, "
         "uses inside OS-dependent data dir (usually $HOME/.local/share/pyldraw)",
    required=False
)
def generate(destination, force):
    if destination is None:
        destination = os.path.join(get_data_dir(), "generated")
    rw_config = Config.load()
    rw_config.generated_path = destination
    rw_config.write()

    try:
        do_generate(rw_config, force, False)
    except UnwritableOutput:
        print(f"{destination} is unwritable, select another output directory")


@main.command()
def config():
    print(yaml.dump(LibraryImporter.config.__dict__))


@main.command()
@click.option("--version", default="latest", type=click.Choice(choices=UPDATES))
@click.option("--yes", is_flag=True, help="use as the library for subsequent uses of pyLdraw ")
def download(version, yes):
    """ download zip/exe, mklist, main function"""
    do_download(version)

    if yes or prompt("use as the version for subsequent uses of pyLdraw ?"):
        ldraw_library_path = os.path.join(get_cache_dir(), version, "ldraw")
        rw_config = Config.load()
        rw_config.ldraw_library_path = ldraw_library_path
        rw_config.write()


if __name__ == "__main__":
    main()
