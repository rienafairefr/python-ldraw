import imp
import importlib
import os
import sys
from contextlib import contextmanager
from importlib.machinery import FileFinder
from importlib.util import spec_from_file_location

from ldraw.config import get_config
from ldraw.generation.generation import do_generate
from ldraw.utils import ensure_exists


def add_sys_path(path_to_add):
    @contextmanager
    def inner():
        _path = sys.path
        sys.path.insert(0, path_to_add)
        yield
        sys.path = _path
    yield inner


class AddSysPath:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass



class CustomImporter:
    """ Added to sys.meta_path as an import hook """

    virtual_module = "ldraw.library"

    @classmethod
    def valid_module(cls, fullname):
        if fullname.startswith(cls.virtual_module):
            rest = fullname[len(cls.virtual_module) :]
            if not rest or rest.startswith("."):
                return True

    def find_module(self, fullname, path=None):  # pylint:disable=unused-argument
        """
        This method is called by Python if this class
        is on sys.path. fullname is the fully-qualified
        name of the module to look for, and path is either
        __path__ (for submodules and subpackages) or None (for
        a top-level module/package).

        Called every time an import
        statement is detected (or __import__ is called), before
        Python's built-in package/module-finding code kicks in.
        """
        if self.valid_module(fullname):
            # As per PEP #302 (which implemented the sys.meta_path protocol),
            # if fullname is the name of a module/package that we want to
            # report as found, then we need to return a loader object.
            # In this simple example, that will just be self.

            return self

        # If we don't provide the requested module, return None, as per
        # PEP #302.

        return None

    @classmethod
    def clean(cls):
        for fullname in list(sys.modules.keys()):
            if cls.valid_module(fullname):
                del sys.modules[fullname]

    def get_code(self, fullname):
        return None

    def load_module(self, fullname):
        """
        This method is called by Python if CustomImporter.find_module
        does not return None. fullname is the fully-qualified name
        of the module/package that was requested.
        """

        if not self.valid_module(fullname):
            # Raise ImportError as per PEP #302 if the requested module/package
            # couldn't be loaded. This should never be reached in this
            # simple example, but it's included here for completeness. :)
            raise ImportError(fullname)

        # if the library already exists and correctly generated,
        # the __hash__ will prevent re-generation
        # JIT generate the library if needed
        config = get_config()
        ldraw_library_path = config.get("ldraw_library_path")
        generated_library_path = config.get("generated_path")
        if generated_library_path is None:
            generated_library_path = ensure_exists(
                os.path.join(ldraw_library_path, "..", "__generated")
            )
        do_generate(generated_library_path)

        with add_sys_path(generated_library_path):
            return importlib.import_module(fullname)

