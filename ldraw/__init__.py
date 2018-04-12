"""
__init__.py - Package file for the ldraw Python package.

Copyright (C) 2008 David Boddie <david@boddie.org.uk>

This file is part of the ldraw Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
import sys
import imp

import os

from ldraw.config import get_config, write_config
from ldraw.library_gen import library_gen_main
from ldraw.dirs import get_data_dir, get_config_dir
from ldraw.download import download_main


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


def load_lib_from(fullname, library_dir):
    """ load library from a dir """
    dot_split = fullname.split('.')
    dot_split.pop(0)
    lib_name = dot_split[-1]
    lib_dir = os.path.join(library_dir, *tuple(dot_split[:-1]))
    info = imp.find_module(lib_name, [lib_dir])
    library_module = imp.load_module(lib_name, *info)
    return library_module


def load_lib(library_path, fullname):
    """ try to load from library """
    return load_lib_from(fullname, library_path)


def try_download_generate_lib():
    # Download the library and generate it, if needed
    config = get_config()
    parts_lst_path = config['parts.lst']
    download_main(parts_lst_path)
    data_dir = get_data_dir()
    library_path = config.get('library')
    if library_path is not None:
        library_gen_main(parts_lst_path, library_path)
        return library_path
    else:
        try:
            # try to write the library to ldraw package folder (can work if user-writeable)
            ldraw_path = os.path.abspath(os.path.dirname(__file__))
            library_gen_main(parts_lst_path, ldraw_path)
            return ldraw_path
        except (OSError, IOError):
            # Failed, then write it to data_dir
            library_gen_main(parts_lst_path, data_dir)
            return data_dir


class CustomImporter(object):
    """ Added to sys.meta_path as an import hook """
    virtual_module = 'ldraw.library'

    @classmethod
    def valid_module(cls, fullname):
        if fullname.startswith(cls.virtual_module):
            rest = fullname[len(cls.virtual_module):]
            if not rest or rest.startswith('.'):
                return True

    def find_module(self, fullname, path=None): # pylint:disable=unused-argument
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
        generated_library_path = try_download_generate_lib()
        mod = load_lib(generated_library_path, fullname)
        sys.modules[fullname] = mod
        return mod


if not any(isinstance(o, CustomImporter) for o in sys.meta_path):
    # Add our import hook to sys.meta_path
    sys.meta_path.insert(0, CustomImporter())
