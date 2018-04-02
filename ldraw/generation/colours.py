#!/usr/bin/env python
"""
Called by ldraw.library_gen to generate the ldraw/library/colours.py file
"""
from __future__ import print_function
import codecs
import os

import pystache

from ldraw.resources import get_resource
from ldraw.utils import clean, camel


def get_c_dict(colour):
    """
    Gets a dict from a Colour object
    """
    return {'code': colour.code,
            'full_name': colour.name,
            'name': camel(clean(colour.name)),
            'alpha': colour.alpha,
            'rgb': colour.rgb, 'colour_attributes': colour.colour_attributes}


def gen_colours(parts, output_dir):
    """
    Generates a colours.py from library data
    """
    print('generate ldraw.library.colours...')

    colours_mustache = get_resource(os.path.join('templates', 'colours.mustache'))
    colours_template_file = codecs.open(colours_mustache, 'r', encoding='utf-8')
    colours_template = pystache.parse(colours_template_file.read())

    context = {'colours': [get_c_dict(c) for c in parts.colours_by_name.values()]}
    context['colours'].sort(key=lambda r: r['code'])

    colours_str = pystache.render(colours_template, context=context)
    library_path = os.path.join(output_dir, 'library')

    colours_py = os.path.join(library_path, 'colours.py')

    with codecs.open(colours_py, 'w', encoding='utf-8') as generated_file:
        generated_file.write(colours_str)
