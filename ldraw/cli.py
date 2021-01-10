import logging
import os
from pprint import pprint

import click
import inquirer
from ldraw.config import select_library_version, get_config, write_config
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
    "--force",
    help="re-generate even if it's apparently not needed",
    required=False,
    is_flag=True,
)
@click.option(
    "--destination",
    help="generate in another dir. ldraw/library folder will be created below that if needed. If not specified, "
         "uses inside OS-dependent data dir (usually $HOME/.local/share)",
    required=False
)
def generate(destination, force):
    if destination is None:
        destination = get_data_dir()
    library_path = os.path.join(os.path.abspath(destination), "ldraw", "library")

    try:
        do_generate(library_path, force, True)
    except UnwritableOutput as e:
        print(f"{library_path} is unwritable, select another output directory")


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    if ctx.invoked_subcommand is None:
        pprint(get_config())


@config.command(name="get")
@click.argument("key")
def get_config(key):
    config_dict = get_config()
    return config_dict.get(key)


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    config_dict = get_config()
    config_dict[key] = value
    write_config(config_dict)


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
