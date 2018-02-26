#!/usr/bin/env python
"""
Generates the ldraw.library.parts namespace
"""
from __future__ import print_function
import codecs
import os
import itertools

from progress.bar import Bar
import pystache

from ldraw.resources import get_resource
from ldraw.utils import clean, camel, ensure_exists, flatten
from ldraw.parts import PartError

PARTS__INIT__TEMPLATE = get_resource(os.path.join('templates', 'parts__init__.mustache'))
PARTS__INIT__TEMPLATE = codecs.open(PARTS__INIT__TEMPLATE, 'r', encoding='utf-8')
PARTS__INIT__TEMPLATE = pystache.parse(PARTS__INIT__TEMPLATE.read())

PARTS_TEMPLATE = get_resource(os.path.join('templates', 'parts.mustache'))
PARTS_TEMPLATE = codecs.open(PARTS_TEMPLATE, 'r', encoding='utf-8')
PARTS_TEMPLATE = pystache.parse(PARTS_TEMPLATE.read())

SECTION_SEP = '|'


def write_section_file(parts_dir, list_of_parts, mod_path):
    """ Writes a single section files"""
    list_of_parts.sort(key=lambda o: o['description'])
    part_str = pystache.render(PARTS_TEMPLATE, context={'parts': list_of_parts})
    parts_py = os.path.join(parts_dir, mod_path)
    ensure_exists(os.path.dirname(parts_py))
    with codecs.open(parts_py, 'w', encoding='utf-8') as generated_file:
        generated_file.write(part_str)


def get_part_dict(parts, description):
    """ Gets a dict context for a part """

    try:
        code = parts.parts_by_name[description]
        #part = parts.part(code=code)
        return {
         #   'path': part.path,
            'description': description,
            'class_name': clean(camel(description)),
            'code': code
        }
    except (PartError, KeyError):
        return {}


def gen_parts(parts, output_dir):
    """
    Generates the ldraw.library.parts namespace
    :param parts: Parts object
    :param output_dir: where to output the library
    :return:
    """
    print('generate ldraw.library.parts, this might take a long time...')

    library_path = os.path.join(output_dir, 'library')
    parts_dir = ensure_exists(os.path.join(library_path, 'parts'))

    sections = _get_sections(parts)

    packages = _get_packages(sections)

    for package_name, modules in packages.items():
        generate_parts__init__(library_path, modules, package_name)

    for section_name, section_parts in sections.items():
        generate_section(parts, parts_dir, section_name, section_parts)


def _get_packages(sections):
    packages = {}
    for section_name in sections:
        rsplitted = section_name.rsplit(SECTION_SEP, 1)
        package = {'module_name': rsplitted[-1]}
        if len(rsplitted) > 1:
            packages.setdefault(rsplitted[0], []).append(package)
        else:
            packages.setdefault('', []).append(package)
    return packages


def _get_sections(parts):
    sections = {}
    for key, value in flatten(parts.parts, sep=SECTION_SEP).items():
        rsplitted = key.rsplit(SECTION_SEP, 1)
        description = rsplitted[-1]
        sections.setdefault(rsplitted[0], {})[description] = value
    return sections


def module_path(section):
    """ gets the .py path from a section name"""
    return section.replace(SECTION_SEP, os.sep) + '.py'


def generate_section(parts, parts_dir, section_name, section_parts):
    """ generate all the sections in ldraw.library.parts namespace"""
    parts_list = []
    progress_bar = Bar('section %s ...' % section_name, max=len(section_parts))
    for description in section_parts:
        parts_list.append(get_part_dict(parts, description))
        progress_bar.next()
    progress_bar.finish()
    parts_list = [x for x in parts_list if x != {}]
    if section_name == 'others':
        parts_list.sort(key=lambda r: r.get('category', 'others'))
        for name, grouped in itertools.groupby(parts_list, key=lambda r: r.get('category', 'others')):
            grouped = list(grouped)
            if name is None:
                name = 'others'

            write_section_file(parts_dir, grouped, module_path(name))
    else:
        write_section_file(parts_dir, parts_list, module_path(section_name))


def generate_parts__init__(library_path, modules, package_name):
    """ generate the appropriate __init__.py to make submodules in ldraw.library.parts """
    parts__init__str = pystache.render(PARTS__INIT__TEMPLATE, context={'sections': modules})
    if package_name == '':
        parts__init__ = os.path.join(library_path, 'parts', '__init__.py')
    else:
        parts__init__ = os.path.join(library_path, 'parts', package_name, '__init__.py')
    ensure_exists(os.path.dirname(parts__init__))
    with codecs.open(parts__init__, 'w', encoding='utf-8') as parts__init__file:
        parts__init__file.write(parts__init__str)
