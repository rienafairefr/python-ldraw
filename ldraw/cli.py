import logging
import os

import click
import inquirer
import yaml

from ldraw import generate as do_generate, LibraryImporter
from ldraw.config import use as do_use, Config
from ldraw.dirs import get_data_dir, get_cache_dir
from ldraw.downloads import download as do_download, UPDATES
from ldraw.generation.exceptions import UnwritableOutput
from ldraw.utils import prompt


@click.group()
@click.option("--debug", is_flag=True)
def main(debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@main.command(
    help="specify which LDraw library version to use"
)
@click.option("--version", type=click.Choice(choices=UPDATES))
def use(version):

    if version is None:
        cache_ldraw = get_cache_dir()

        choices = {
            file: file
            for file in os.listdir(cache_ldraw)
            if os.path.isdir(os.path.join(cache_ldraw, file))
        }
        questions = [
            inquirer.List(
                "Ldraw library Version",
                message="What version do you want to use?",
                choices=choices,
                carousel=True,
            ),
        ]
        result = inquirer.prompt(questions)
        if result is None:
            raise click.Abort('no option selected')
        version = choices[result["Ldraw library Version"]]
    return do_use(version)


@main.command(
    help="generate the ldraw.library modules"
)
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
@click.option("--yes", is_flag=True, help="use as the ldraw.library location for subsequent uses of pyLdraw")
def generate(destination, force, yes):
    if destination is None:
        destination = os.path.join(get_data_dir(), "generated")
    destination = os.path.abspath(destination)
    rw_config = Config.load()
    if rw_config.generated_path != destination:
        if yes or prompt("use that generated library for subsequent uses of pyldraw ldraw.library ?"):
            rw_config.generated_path = destination
            rw_config.write()

    try:
        do_generate(rw_config, force, False)
    except UnwritableOutput:
        print(f"{destination} is unwritable, select another output directory")


@main.command(
    help="show pyldraw current config"
)
def config():
    config = Config.load()
    print(yaml.dump(config.__dict__))


@main.command(
    help="download LDraw library files"
)
@click.option("--version", default="latest", type=click.Choice(choices=UPDATES))
@click.option("--yes", is_flag=True, help="use as the library for subsequent uses of pyLdraw")
def download(version, yes):
    release_id = do_download(version)

    rw_config = Config.load()
    ldraw_library_path = os.path.join(get_cache_dir(), release_id)
    if rw_config.ldraw_library_path != ldraw_library_path:
        if yes or prompt("use as the version for subsequent uses of pyLdraw ?"):
            rw_config.ldraw_library_path = ldraw_library_path
            rw_config.write()


if __name__ == "__main__":
    main()
