import logging
import os
from pprint import pprint

import click
import inquirer
from ldraw.config import select_library_version, get_config
from ldraw.dirs import get_data_dir
from ldraw.download import do_download, cache_ldraw, UPDATES
from ldraw.generation.generation import do_generate
from ldraw.generation.eceptions import UnwritableOutput

from ldraw.utils import prompt, ensure_exists


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
    if version is not None:
        ldraw_library_path = os.path.join(cache_ldraw, version)
        if not os.path.exists(ldraw_library_path):
            print("downloading that version to use...")
            do_download(version)
    else:

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
            return
        ldraw_library_path = os.path.join(
            cache_ldraw, choices[result["Ldraw library Version"]], "ldraw"
        )

    select_library_version(ldraw_library_path)


@main.command()
@click.option(
    "--in-tree",
    help="write where the ldraw module is",
    required=False,
    is_flag=True,
)
@click.option(
    "--force",
    help="re-generate even if it's apparently not needed",
    required=False,
    is_flag=True,
)
def generate(in_tree, force):
    if in_tree:
        library_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'library'))
    else:
        library_path = ensure_exists(get_config().get('generated_library_path', os.path.join(get_data_dir(), "ldraw", "library")))
    try:
        do_generate(library_path, force, True)
    except UnwritableOutput as e:
        print(f"{library_path} is unwritable, select another output directory")


@main.command()
def config():
    pprint(get_config())


@main.command()
@click.option("--version", default="latest", type=click.Choice(choices=UPDATES))
@click.option("--yes", is_flag=True, help="use as the library for subsequent uses of pyLdraw ")
def download(version, yes):
    """ download zip/exe, mklist, main function"""
    do_download(version)

    if yes or prompt("use as the version for subsequent uses of pyLdraw ?"):
        select_library_version(os.path.join(cache_ldraw, version, "ldraw"))


if __name__ == "__main__":
    main()
