""" ldraw.library generation """
import os
import shutil
import hashlib

from ldraw.dirs import get_data_dir
from ldraw.generation.colours import gen_colours
from ldraw.generation.parts import gen_parts
from ldraw.parts import Parts
from ldraw.utils import ensure_exists


def library_gen_main(parts_lst, output_dir):
    library_path = os.path.join(output_dir, 'library')
    ensure_exists(library_path)
    hash_path = os.path.join(library_path, '__hash__')

    md5_parts_lst = hashlib.md5(open(parts_lst, 'rb').read()).hexdigest()

    if os.path.exists(hash_path):
        md5 = open(hash_path, 'r').read()
        if md5 == md5_parts_lst:
            return

    parts = Parts(parts_lst)

    gen_colours(parts, output_dir)
    gen_parts(parts, output_dir)

    library__init__ = os.path.join(library_path, '__init__.py')

    with open(library__init__, 'w') as library__init__:
        library__init__.write("""\"\"\" the ldraw.library module, auto-generated \"\"\"
__all__ = [\'colours\']
""")
    shutil.copy('ldraw-license.txt', os.path.join(library_path, 'license.txt'))

    open(hash_path, 'w').write(md5_parts_lst)


if __name__ == '__main__':
    library_gen_main(os.path.join(get_data_dir(), 'ldraw', 'parts.lst'), 'ldraw')
