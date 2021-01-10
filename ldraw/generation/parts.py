#!/usr/bin/env python
"""
Generates the ldraw.library.parts namespace
"""
import codecs
import os

from progress.bar import Bar
import pystache

from ldraw.resources import get_resource_content
from ldraw.utils import clean, camel, ensure_exists, flatten, flatten2
from ldraw.parts import PartError

PARTS__INIT__TEMPLATE = pystache.parse(get_resource_content(
    os.path.join("templates", "parts__init__.mustache")
))

PARTS_TEMPLATE = pystache.parse(get_resource_content(os.path.join("templates", "parts.mustache")))

SECTION_SEP = '#|#'


def write_section_file(parts_dir, list_of_parts, mod_path):
    """ Writes a single section files"""
    list_of_parts.sort(key=lambda o: o["description"])
    part_str = pystache.render(PARTS_TEMPLATE, context={"parts": list_of_parts})
    parts_py = os.path.join(parts_dir, mod_path)
    ensure_exists(os.path.dirname(parts_py))
    with codecs.open(parts_py, "w", encoding="utf-8") as generated_file:
        generated_file.write(part_str)


def get_part_dict(parts, description):
    """ Gets a dict context for a part """

    try:
        code = parts.parts_by_name[description]
        # part = parts.part(code=code)
        return {
            #   'path': part.path,
            "description": description,
            "class_name": clean(camel(description)),
            "code": code,
        }
    except (PartError, KeyError):
        return {}


def gen_parts(parts, library_path):
    """
    Generates the ldraw.library.parts namespace
    :param parts: Parts object
    :param output_dir: where to output the library
    :return:
    """
    print("generate ldraw.library.parts, this might take a long time...")

    parts_dir = ensure_exists(os.path.join(library_path, "parts"))

    sections = {}
    sections2 = {}
    for key, value in flatten(parts.parts, sep=SECTION_SEP).items():
        rsplitted = key.rsplit(SECTION_SEP, 1)
        description = rsplitted[-1]
        sections.setdefault(rsplitted[0], {})[description] = value

    for key, value in flatten2(parts.parts).items():
        sections2.setdefault(key[:-1], {})[key[-1]] = value

    packages = {}
    packages2 = {}
    # for name in sections:
    #     rsplitted = name.rsplit(SECTION_SEP, 1)
    #     package = {'module_name': rsplitted[-1]}
    #     if len(rsplitted) > 1:
    #         packages.setdefault(rsplitted[0], []).append(package)
    #     else:
    #         packages.setdefault('', []).append(package)

    for key in sections2:
        package = {'module_name': key[-1]}
        if len(key) > 1:
            packages2.setdefault(key[0], []).append(package)
        else:
            packages2.setdefault('', []).append(package)

    case2 = []

    #for package_name, modules in packages.items():
    #    if package_name == '':
    #        module_parts = parts.parts_by_category[''].keys()
    #    else:
    #        module_parts = sections.get(SECTION_SEP.join((package_name, '')), {}).keys()
    #    modules = list(filter(lambda m: m['module_name'] != '', modules))
    #    case1.append((library_path, modules, list(module_parts), package_name))
    #    #generate_parts__init__(parts, library_path, modules, module_parts, package_name)

    for package_name, modules in packages2.items():
        if len(package_name) == 0:
            module_parts = parts.parts_by_category[''].keys()
        else:
            module_parts = sections.get(SECTION_SEP.join((package_name, '')), {}).keys()
        modules = list(filter(lambda m: m['module_name'] != '', modules))
        case2.append((library_path, modules, list(module_parts), package_name))
        #generate_parts__init__(parts, library_path, modules, module_parts, package_name)

    #for section_name, section_parts in sections.items():
    #    generate_section(parts, parts_dir, section_name, section_parts)

    for section_name, section_parts in sections2.items():
        generate_section(parts, parts_dir, section_name, section_parts)


def generate_section(parts, parts_dir, section_key, section_parts):
    """ generate all the sections in ldraw.library.parts namespace"""
    parts_list = []
    progress_bar = Bar("section %s ..." % str(section_key), max=len(section_parts))
    for description in section_parts:
        parts_list.append(get_part_dict(parts, description))
        progress_bar.next()
    progress_bar.finish()
    parts_list = [x for x in parts_list if x != {}]
    write_section_file(parts_dir, parts_list, os.path.join(*section_key) + '.py')


def generate_parts__init__(parts, library_path, modules, module_parts, package_name):
    """ generate the appropriate __init__.py to make submodules in ldraw.library.parts """
    parts_list = []
    for description in module_parts:
        parts_list.append(get_part_dict(parts, description))
    parts__init__str = pystache.render(PARTS__INIT__TEMPLATE, context={'sections': modules, 'parts': parts_list})
    if package_name == '':
        parts__init__ = os.path.join(library_path, 'parts', '__init__.py')
    else:
        parts__init__ = os.path.join(library_path, 'parts', package_name, '__init__.py')
    ensure_exists(os.path.dirname(parts__init__))
    with codecs.open(parts__init__, 'w', encoding='utf-8') as parts__init__file:
        parts__init__file.write(parts__init__str)
