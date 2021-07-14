"""
takes care of reading and writing a configuration in config.yml
"""
import os
import typing

import inquirer
import yaml

from ldraw import download
from ldraw.dirs import get_cache_dir, get_config_dir


CONFIG_FILE = os.path.join(get_config_dir(), 'config.yml')


class Config:
    ldraw_library_path: typing.Optional[str]
    generated_path: typing.Optional[str]

    def __init__(self, ldraw_library_path=None, generated_path=None):
        self.ldraw_library_path = ldraw_library_path
        self.generated_path = generated_path

    @classmethod
    def load(cls, config_file=None):
        if config_file is None:
            config_file = CONFIG_FILE
        with open(config_file, "r") as config_file:
            cfg = yaml.load(config_file, Loader=yaml.SafeLoader)
            return cls(
                ldraw_library_path=cfg.get('ldraw_library_path'),
                generated_path=cfg.get('generated_path')
            )

    def write(self, config_file=None):
        """ write the config to config.yml """
        if config_file is None:
            config_file = CONFIG_FILE
        with open(config_file, "w") as config_file:
            written = {}
            if self.ldraw_library_path is not None: written['ldraw_library_path'] = self.ldraw_library_path
            if self.generated_path is not None: written['generated_path'] = self.generated_path
            yaml.dump(written, config_file)


def select_library_version(ldraw_library_path, config: Config):
    config.ldraw_library_path = ldraw_library_path
    config.write()


def use(version):
    from ldraw import LibraryImporter
    cache_ldraw = get_cache_dir()
    if version is not None:
        ldraw_library_path = os.path.join(cache_ldraw, version)
        if not os.path.exists(ldraw_library_path):
            print("downloading that version to use...")
            download(version)
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

    config = LibraryImporter.config
    config.ldraw_library_path = ldraw_library_path
