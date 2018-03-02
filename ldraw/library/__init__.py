import os
import pkgutil

import sys

from ldraw import get_data_dir

data_dir = get_data_dir()

library_path = os.path.join(data_dir, 'library')


# import all
def import_all(pkg_dir):
    modules = {}
    """Looks into the given path for modules and imports them"""
    for (module_loader, name, _) in pkgutil.iter_modules([pkg_dir]):
        modules[name] = module_loader.find_module(name).load_module(name)
    return modules

mods = import_all(library_path)

colours = mods.get('colours')
if colours:
    sys.modules['ldraw.library.colours'] = colours

parts = mods.get('parts')
if parts:
    sys.modules['ldraw.library.parts'] = parts
