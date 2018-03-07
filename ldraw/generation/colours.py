#!/usr/bin/env python
import codecs
import os

import pystache


from ldraw.utils import clean, camel, ensure_exists


def gen_colours(parts, output_dir, force=False):
    """
    try:
        from ldraw.library.colours import Colour
        if not force:
            return
    except ImportError, e:
        pass
"""
    print('generate ldraw.library.colours...')

    colours_template_data = codecs.open(os.path.join('templates', 'colours.mustache'), 'r', encoding='utf-8').read()
    colours_template = pystache.parse(colours_template_data)

    def get_c_dict(c):
        return {'code': c.code,
                'full_name': c.name,
                'name': camel(clean(c.name)),
                'alpha': c.alpha,
                'rgb': c.rgb, 'colour_attributes': c.colour_attributes}

    context = {'colours': [get_c_dict(c) for c in parts.colours_by_name.values()]}
    context['colours'].sort(key=lambda r: r['code'])

    colours_str = pystache.render(colours_template, context=context)
    library_path = ensure_exists(os.path.join(output_dir, 'library'))

    colours_py = os.path.join(library_path, 'colours.py')

    with codecs.open(colours_py, 'w', encoding='utf-8') as generated_file:
        generated_file.write(colours_str)

    __init__ = os.path.join(library_path, '__init__.py')
    with open(__init__, 'w') as __init__:
        __init__.write('__all__ = [\'colours\']')
