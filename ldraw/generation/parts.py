#!/usr/bin/env python
import codecs
import os

import itertools
from progress.bar import Bar

import pystache

from ldraw.utils import clean, camel, ensure_exists


def gen_parts(parts, output_dir, force=False):
    """
    try:
        from ldraw.library.colours import ColoursByCode
        if not force:
            return
    except ImportError, e:
        gen_colours(parts, config, data_dir)
        from ldraw import library
        imp.reload(library)
        from ldraw.library.colours import ColoursByCode

    try:
        from ldraw.library.parts import Part
        if not force:
            return
    except ImportError:
        pass
"""
    print('generate ldraw.library.parts, this might take a long time...')

    parts_template = codecs.open(os.path.join('templates', 'parts.mustache'), 'r', encoding='utf-8').read()
    parts_template = pystache.parse(parts_template)

    def get_part_dict(description):
        try:
            code = parts.parts[description]
            part = parts.part(code=code)
            return {
                'path': part.path,
                'category': part.category,
                'description': description,
                'class_name': clean(camel(description)),
                'code': code
            }
        except:
            return {}

    def module_name(section):
        return clean(section.lower()) + ('s' if not section.endswith('s') else '')

    def get_section_dict(row):
        section = row[0]
        parts_list = row[1]
        return {'name': section,
                'module_name': module_name(section),
                'parts': parts_list}

    sections = list(map(get_section_dict, parts.extra_sections.items()))
    sections.extend(list(map(get_section_dict, parts.sections.items())))
    library_path = ensure_exists(os.path.join(output_dir, 'library'))

    parts_dir = os.path.join(library_path, 'parts')
    try:
        os.makedirs(parts_dir)
    except:
        pass

    for sec in sections:

        parts_list = []
        bar = Bar('section %s ...' % sec['name'], max=len(sec['parts']))
        for description in sec['parts']:
            parts_list.append(get_part_dict(description))
            bar.next()
        bar.finish()

        parts_list = [x for x in parts_list if x != {}]

        def write_section_file(list_of_parts, mod_name):
            list_of_parts.sort(key=lambda o: o['description'])
            part_str = pystache.render(parts_template, context={'parts': list_of_parts})
            parts_py = os.path.join(parts_dir, mod_name + '.py')
            with codecs.open(parts_py, 'w', encoding='utf-8') as generated_file:
                generated_file.write(part_str)


        if sec['name'] == 'Others':
            parts_list.sort(key=lambda r: r.get('category'))
            for name, grouped in itertools.groupby(parts_list, key=lambda r: r.get('category')):
                grouped = list(grouped)
                if name is None:
                    name = 'others'
                mod_name = module_name(name)

                write_section_file(grouped, mod_name)
        else:
            write_section_file(parts_list, sec['module_name'])

    parts__init__template = codecs.open(os.path.join('templates', 'parts__init__.mustache'), 'r',
                                        encoding='utf-8').read()
    parts__init__template = pystache.parse(parts__init__template)

    parts__init__str = pystache.render(parts__init__template, context={'sections': sections})
    parts__init__ = os.path.join(library_path, 'parts', '__init__.py')
    with codecs.open(parts__init__, 'w', encoding='utf-8') as parts__init__file:
        parts__init__file.write(parts__init__str)
