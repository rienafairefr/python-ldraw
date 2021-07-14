"""
Module tasked with generating python files for the ldraw.library namespace
"""
import hashlib
import os
import shutil
import sys
import traceback

import typing

from ldraw.config import Config
from ldraw.generation.colours import gen_colours
from ldraw.generation.exceptions import NoLibrarySelected, UnwritableOutput
from ldraw.generation.parts import gen_parts
from ldraw.parts import Parts
from ldraw.resources import get_resource, get_resource_content
from ldraw.utils import ensure_exists

memoized = {}


def generate(config: typing.Optional[Config] = None, force=False, warn=True):
    """ main function for the library generation """
    try:
        generated_library_path = os.path.join(config.generated_path, "library")
        ensure_exists(generated_library_path)

        hash_path = os.path.join(generated_library_path, "__hash__")

        library_path = config.ldraw_library_path

        parts_lst = os.path.join(library_path, "ldraw", "parts.lst")
        md5_parts_lst = hashlib.md5(open(parts_lst, "rb").read()).hexdigest()

        if os.path.exists(hash_path):
            md5 = open(hash_path, "r").read()
            if md5 == md5_parts_lst and not force:
                return

        shutil.rmtree(generated_library_path)
        ensure_exists(generated_library_path)

        parts = Parts(parts_lst)

        library__init__ = os.path.join(generated_library_path, "__init__.py")

        with open(library__init__, "w") as library__init__:
            library__init__.write(LIBRARY_INIT)

        shutil.copy(
            get_resource("ldraw-license.txt"),
            os.path.join(generated_library_path, "license.txt"),
        )

        gen_colours(parts, generated_library_path)
        gen_parts(parts, generated_library_path)

        open(hash_path, "w").write(md5_parts_lst)
    except OSError as exc:
        traceback.print_exc(exc)
        raise UnwritableOutput(
            f"can't write the output directory {generated_library_path}"
        ) from exc


LIBRARY_INIT = get_resource_content(os.path.join("templates", "ldraw__init__"))
