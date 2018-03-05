#!/usr/bin/env python
import os

from ldraw.config import get_config
from ldraw.generate.colours import gen_colours
from ldraw.generate.parts import gen_parts
from ldraw.parts import Parts


def generate_main(data_dir):
    config = get_config()

    try:
        os.makedirs(os.path.join(data_dir, 'library'))
    except:
        pass

    p = Parts(config['parts.lst'])

    gen_colours(p, config, data_dir)
    gen_parts(p, config, data_dir)


if __name__ == '__main__':
    generate_main('ldraw')