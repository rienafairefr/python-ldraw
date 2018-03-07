import os
import shutil

from ldraw.dirs import get_data_dir
from ldraw.generation.colours import gen_colours
from ldraw.generation.parts import gen_parts
from ldraw.parts import Parts


def library_gen_main(parts_lst, data_dir):
    library_path = os.path.join(data_dir, 'library')
    shutil.rmtree(library_path, ignore_errors=True)

    p = Parts(parts_lst)

    gen_colours(p, data_dir)
    gen_parts(p, data_dir)
    shutil.copy('ldraw-license.txt', os.path.join(library_path, 'license.txt'))


if __name__ == '__main__':
    library_gen_main(os.path.join(get_data_dir(), 'ldraw', 'parts.lst'), 'ldraw')