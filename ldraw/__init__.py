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
import os

import imp


from ldraw.generation import generate_main
from ldraw.dirs import get_data_dir, get_config_dir
from ldraw.download import download_main

config_dir = get_config_dir()
data_dir = get_data_dir()


__ok_generated = os.path.join(data_dir, '__ok_generated')
if not os.path.exists(__ok_generated):
    dowload_library_main(data_dir)
    generate_main(data_dir)

    from ldraw import library
    imp.reload(library)

    from library.colours import Black
    from library.parts.others import _Brick1X1

    open(__ok_generated, 'w').close()

        # If we don't provide the requested module, return None, as per
        # PEP #302.

        return None

    def load_module(self, fullname):
        """This method is called by Python if CustomImporter.find_module
           does not return None. fullname is the fully-qualified name
           of the module/package that was requested."""

        if fullname != self.virtual_module:
            # Raise ImportError as per PEP #302 if the requested module/package
            # couldn't be loaded. This should never be reached in this
            # simple example, but it's included here for completeness. :)
            raise ImportError(fullname)

        # PEP#302 says to return the module if the loader object (i.e,
        # this class) successfully loaded the module.
        # Note that a regular class works just fine as a module.

        def load_lib():
            info = imp.find_module('library', [data_dir])
            library_module = imp.load_module('library', *info)
            return library_module

        try:
            return load_lib()
        except ImportError, e:
            generate_main(data_dir)
            download_main(data_dir)
            return load_lib()


# Add our import hook to sys.meta_path
sys.meta_path.append(CustomImporter())

from library.colours import Black
from library.parts.others import _Brick1X1

from ldraw.library.colours import Black
from ldraw.library.parts.others import _Brick1X1
