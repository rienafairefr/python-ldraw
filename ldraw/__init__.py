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
import sys

from pkg_resources import get_distribution, DistributionNotFound

from ldraw.downloads import download
from ldraw.config import use
from ldraw.generation import generate
from ldraw.imports import LibraryImporter

__all__ = [
    download, generate, use
]

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


if LibraryImporter not in sys.meta_path:
    # Add our import hook to sys.meta_path
    sys.meta_path.insert(0, LibraryImporter)

if __name__ == '__main__':
    from ldraw import cli
    cli.main()
