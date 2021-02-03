import imp
import os
import sys

from ldraw import download, generate
from ldraw.config import Config
from ldraw.dirs import get_data_dir
from ldraw.downloads import cache_ldraw
from ldraw.generation import NoLibrarySelected

VIRTUAL_MODULE = 'ldraw.library'


def load_lib(library_path, fullname):
    # Use importlib if python 3.4+, else imp
    #if sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 4):
    #    # submodule_name = fullname[len("ldraw") + 1:]
    #    from importlib.machinery import FileFinder, SourceFileLoader, SOURCE_SUFFIXES
    #    file_finder = FileFinder(library_path, (SourceFileLoader, SOURCE_SUFFIXES))
#
    #    result = file_finder.find_spec(fullname)
    #    return result.loader.load_module(fullname)
    #else:
    dot_split = fullname.split('.')
    dot_split.pop(0)
    lib_name = dot_split[-1]
    lib_dir = os.path.join(library_path, *tuple(dot_split[:-1]))
    info = imp.find_module(lib_name, [lib_dir])
    library_module = imp.load_module(lib_name, *info)

    return library_module


def try_download_generate_lib():
    # Download the library and generate it, if needed
    config = Config.get()
    if config is None:
        config = Config.load()

    ldraw_library_path = config.ldraw_library_path
    if ldraw_library_path is None:
        download("latest")
        config.ldraw_library_path = os.path.join(cache_ldraw, "latest")

    generated_path = config.generated_path
    if generated_path is None:
        generated_path = os.path.join(get_data_dir(), 'generated')
    if "LDRAW_GENERATED_PATH" in os.environ:
        generated_path = os.environ['LDRAW_GENERATED_PATH']
    generate(config)
    return generated_path


class LibraryImporter:
    """ Added to sys.meta_path as an import hook """

    @classmethod
    def valid_module(cls, fullname):
        if fullname.startswith(VIRTUAL_MODULE):
            rest = fullname[len(VIRTUAL_MODULE):]
            if not rest or rest.startswith('.'):
                return True

    @classmethod
    def find_module(cls, fullname, path=None):  # pylint:disable=unused-argument
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
        if cls.valid_module(fullname):
            # As per PEP #302 (which implemented the sys.meta_path protocol),
            # if fullname is the name of a module/package that we want to
            # report as found, then we need to return a loader object.
            # In this simple example, that will just be self.

            return cls()

        # If we don't provide the requested module, return None, as per
        # PEP #302.

        return None

    @classmethod
    def clean(cls):
        for fullname in list(sys.modules.keys()):
            if cls.valid_module(fullname):
                del sys.modules[fullname]
        if 'ldraw' in sys.modules and 'library' in sys.modules['ldraw'].__dict__:
            del sys.modules['ldraw'].library

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
        generated_library_path = try_download_generate_lib()
        mod = load_lib(generated_library_path, fullname)
        sys.modules[fullname] = mod
        return mod


