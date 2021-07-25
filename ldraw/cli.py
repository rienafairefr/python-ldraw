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


@main.command()
@click.option("--version", type=click.Choice(choices=UPDATES))
def use(version):
    if version is None:
        cache_ldraw = get_cache_dir()

        def get_choice(file):
            abs_ = os.path.join(cache_ldraw, file)
            if file == "latest":
                release_id = str(open(os.path.join(abs_, "release_id")).read())
                return f"latest ({release_id})"
            else:
                return file

        choices = {
            get_choice(file): file
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
    config = Config.load()
    print(yaml.dump(config.__dict__))


@main.command()
@click.option("--version", default="latest", type=click.Choice(choices=UPDATES))
@click.option("--yes", is_flag=True, help="use as the library for subsequent uses of pyLdraw ")
def download(version, yes):
    """ download zip/exe, mklist, main function"""
    do_download(version)

    if yes or prompt("use as the version for subsequent uses of pyLdraw ?"):
        ldraw_library_path = os.path.join(get_cache_dir(), version)
        rw_config = Config.load()
        rw_config.ldraw_library_path = ldraw_library_path
        rw_config.write()


if __name__ == "__main__":
    main()
