import hashlib
import os
import shutil

from ldraw.config import get_config
from ldraw.generation.exceptions import NoLibrarySelected
from ldraw.resources import get_resource, get_resource_content

from ldraw.utils import ensure_exists

from ldraw.generation.eceptions import UnwritableOutput
from ldraw.generation.parts import gen_parts

from ldraw.generation.colours import gen_colours

from ldraw.parts import Parts


def do_generate(library_output_path, force=False, cli=False):
    """ main function for the library generation """
    try:
        ensure_exists(library_output_path)

        hash_path = os.path.join(library_output_path, "__hash__")

        config = get_config()
        try:
            library_path = config["ldraw_library_path"]
        except KeyError:
            raise NoLibrarySelected()

        parts_lst = os.path.join(library_path, "parts.lst")
        md5_parts_lst = hashlib.md5(open(parts_lst, "rb").read()).hexdigest()

        if os.path.exists(hash_path):
            md5 = open(hash_path, "r").read()
            if md5 == md5_parts_lst and not force:
                if cli:
                    print("already generated, add --force to re-generate")
                return

        shutil.rmtree(library_output_path)
        ensure_exists(library_output_path)

        parts = Parts(parts_lst)

        library__init__ = os.path.join(library_output_path, "__init__.py")

        with open(library__init__, "w") as library__init__:
            library__init__.write(LIBRARY_INIT)

        shutil.copy(
            get_resource("ldraw-license.txt"),
            os.path.join(library_output_path, "license.txt"),
        )

        gen_colours(parts, library_output_path)
        gen_parts(parts, library_output_path)

        open(hash_path, "w").write(md5_parts_lst)
    except OSError as exc:
        raise UnwritableOutput(
            f"can't write the output directory {library_output_path}"
        ) from exc


LIBRARY_INIT = get_resource_content(os.path.join("templates", "ldraw__init__"))
