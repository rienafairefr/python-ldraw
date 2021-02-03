#!/usr/bin/env python
"""
Generates the ldraw.library.parts namespace
"""
import codecs
import os
import sys

import pystache
from attrdict import AttrDict
from progress.bar import Bar

from ldraw.parts import PartError
from ldraw.resources import get_resource_content
from ldraw.utils import ensure_exists, flatten2, clean, camel

SECTION_SEP = '#|#'


def gen_parts(parts, library_path):
    sys.stderr.write("generate ldraw.library.parts, this might take a long time...")
    parts_dir = ensure_exists(os.path.join(library_path, "parts"))

    recursive_gen_parts(parts.parts, parts_dir)


def recursive_gen_parts(parts_parts, directory):

    for name, value in list(parts_parts.items()):
        if isinstance(value, AttrDict):
            recurse = False
            for k,v in value.items():
                if len(v) > 0:
                    recurse = True

            if recurse:
                subdir = os.path.join(directory, name)
                ensure_exists(subdir)
                recursive_gen_parts(value, subdir)

    sections = {
        name: value for name, value in parts_parts.items() if not isinstance(value, AttrDict)
    }

    module_parts = {}
    for section_name, section_parts in sections.items():
        if section_name == '':
            continue
        for desc, code in section_parts.items():
            module_parts[desc] = code

        parts_py = os.path.join(directory, f"{section_name}.py")
        part_str = section_content(section_parts, section_name)
        with codecs.open(parts_py, "w", encoding="utf-8") as generated_file:
            generated_file.write(part_str)

    generate_parts__init__(module_parts, directory, sections, parts_parts)


def generate_parts__init__(module_parts, directory, sections, parts_parts):
    """ generate the appropriate __init__.py to make submodules in ldraw.library.parts """
    parts__init__str = parts__init__content(sections)

    parts__init__ = os.path.join(directory, '__init__.py')
    ensure_exists(os.path.dirname(parts__init__))

    with codecs.open(parts__init__, 'w', encoding='utf-8') as parts__init__file:
        parts__init__file.write(parts__init__str)


def parts__init__content(sections):
    sections = [
        {"module_name": module_name} for module_name in sections if module_name != ''
    ]
    return pystache.render(PARTS__INIT__TEMPLATE, context={'sections': sections})


def section_content(section_parts, section_key):
    parts_list = []
    progress_bar = Bar("section %s ..." % str(section_key), max=len(section_parts))
    for description in section_parts:
        parts_list.append(get_part_dict(section_parts, description))
        progress_bar.next()
    progress_bar.finish()
    parts_list = [x for x in parts_list if x != {}]
    parts_list.sort(key=lambda o: o["description"])
    part_str = pystache.render(PARTS_TEMPLATE, context={"parts": parts_list})
    return part_str


PARTS__INIT__TEMPLATE = pystache.parse(get_resource_content(
    os.path.join("templates", "parts__init__.mustache")
))
PARTS_TEMPLATE = pystache.parse(get_resource_content(os.path.join("templates", "parts.mustache")))


def get_part_dict(parts_parts, description):
    """ Gets a dict context for a part """

    try:
        code = parts_parts[description]
        # part = parts.part(code=code)
        return {
            #   'path': part.path,
            "description": description,
            "class_name": clean(camel(description)),
            "code": code,
        }
    except (PartError, KeyError):
        return {}