#!/usr/bin/env python
import codecs
import os
import itertools

from progress.bar import Bar
import pystache
import inflect

from ldraw.utils import clean, camel, ensure_exists, flatten

p = inflect.engine()


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
            code = parts.parts_by_name[description]
            part = parts.part(code=code)
            return {
                'path': part.path,
                'description': description,
                'class_name': clean(camel(description)),
                'code': code
            }
        except Exception, e:
            return {}

    sections = {}
    for k, v in flatten(parts.parts, sep='|').items():
        rsplitted = k.rsplit('|', 1)
        description = rsplitted[-1]
        sections.setdefault(rsplitted[0], {})[description] = v

    library_path = ensure_exists(os.path.join(output_dir, 'library'))
    parts_dir = ensure_exists(os.path.join(library_path, 'parts'))

    packages = {}
    for section_name in sections:
        rsplitted = section_name.rsplit('|', 1)
        package = {'module_name': rsplitted[-1]}
        if len(rsplitted) > 1:
            packages.setdefault(rsplitted[0], []).append(package)
        else:
            packages.setdefault('', []).append(package)

    for package_name, modules in packages.items():
        parts__init__template = codecs.open(os.path.join('templates', 'parts__init__.mustache'), 'r',
                                            encoding='utf-8').read()
        parts__init__template = pystache.parse(parts__init__template)

        parts__init__str = pystache.render(parts__init__template, context={'sections': modules})
        if package_name == '':
            parts__init__ = os.path.join(library_path, 'parts', '__init__.py')
        else:
            parts__init__ = os.path.join(library_path, 'parts', package_name, '__init__.py')
        ensure_exists(os.path.dirname(parts__init__))
        with codecs.open(parts__init__, 'w', encoding='utf-8') as parts__init__file:
            parts__init__file.write(parts__init__str)

    for section_name, section_parts in sections.items():
        parts_list = []
        bar = Bar('section %s ...' % section_name, max=len(section_parts))
        for description in section_parts:
            parts_list.append(get_part_dict(description))
            bar.next()
        bar.finish()

        parts_list = [x for x in parts_list if x != {}]

        def module_name(section):
            return section.replace('|', os.sep)

        def write_section_file(list_of_parts, mod_name):
            list_of_parts.sort(key=lambda o: o['description'])
            part_str = pystache.render(parts_template, context={'parts': list_of_parts})
            parts_py = os.path.join(parts_dir, mod_name + '.py')
            ensure_exists(os.path.dirname(parts_py))
            with codecs.open(parts_py, 'w', encoding='utf-8') as generated_file:
                generated_file.write(part_str)

        if section_name == 'others':
            parts_list.sort(key=lambda r: r.get('category'))
            for name, grouped in itertools.groupby(parts_list, key=lambda r: r.get('category')):
                grouped = list(grouped)
                if name is None:
                    name = 'others'

                write_section_file(grouped, module_name(name))
        else:
            write_section_file(parts_list, module_name(section_name))
