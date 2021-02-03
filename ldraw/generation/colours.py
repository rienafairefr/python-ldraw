#!/usr/bin/env python
"""
Called by ldraw.library_gen to generate the ldraw/library/colours.py file
"""
import codecs
import os
import sys

import pystache

from ldraw.resources import get_resource_content
from ldraw.utils import camel, clean


def gen_colours(parts, library_path):
    """
    Generates a colours.py from library data
    """
    sys.stderr.write("generate ldraw.library.colours...")

    colours_str = colours_module_content(parts)
    colours_py = os.path.join(library_path, "colours.py")
    with codecs.open(colours_py, "w", encoding="utf-8") as generated_file:
        generated_file.write(colours_str)


def colours_module_content(parts):
    colours_mustache = get_resource_content(os.path.join("templates", "colours.mustache"))
    colours_template = pystache.parse(colours_mustache)
    context = {"colours": [get_c_dict(c) for c in parts.colours_by_name.values()]}
    context["colours"].sort(key=lambda r: r["code"])
    colours_str = pystache.render(colours_template, context=context)
    return colours_str


def get_c_dict(colour):
    """
    Gets a dict from a Colour object
    """
    return {
        "code": colour.code,
        "full_name": colour.name,
        "name": camel(clean(colour.name)),
        "alpha": colour.alpha,
        "rgb": colour.rgb,
        "colour_attributes": colour.colour_attributes,
    }