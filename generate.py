#!/usr/bin/env python
import codecs
import json
import random
import re
import os

from ldraw.parts import Parts
import pystache

from ldraw.utils import JsonEncoder, JsonDecoder, clean, camel

p = Parts('tmp/ldraw/parts.lst')

colours_template_data = codecs.open(os.path.join('templates', 'colours.mustache'), 'r', encoding='utf-8').read()
colours_template = pystache.parse(colours_template_data)

context = {'colours': [{'code': c.code, 'name': camel(clean(c.name)),
                        'alpha': c.alpha,
                        'rgb': c.rgb, 'colour_attributes': c.colour_attributes} for c in p.colours_list]}

colours_str = pystache.render(colours_template, context=context)
colours_py = os.path.join('ldraw', 'library', 'colours.py')

with codecs.open(colours_py, 'w', encoding='utf-8') as generated_file:
    generated_file.write(colours_str)

exit(0)

parts_template = codecs.open(os.path.join('templates', 'metaparts.mustache'), 'r', encoding='utf-8').read()
parts_template = pystache.parse(parts_template)


def get_parts():
    parts = random.sample(p.parts.keys(), 100)
    for description in parts:
        try:
            code = p.parts[description]
            part = p.part(code=code)
            yield {
                'part': part,
                'description': description,
                'class_name': clean(camel(description))
            }
            print('treated %s' % description)
        except Exception, e:
            print('ignored an invalid part %s %s %s' % (description, e, e.message))


def get_part_dict(description):
    code = p.parts[description]
    return {
        'description': description,
        'class_name': clean(camel(description)),
        'code': code
    }


parts_json = 'tmp/parts.json'

sections = tuple(p.sections.items())

for section, parts in sections:
    parts_list = [get_part_dict(description) for description in parts]
    parts_list = sorted(parts_list, key=lambda o: o['description'])
    part_str = pystache.render(parts_template, context={'parts': parts_list})
    parts_py = os.path.join('ldraw', 'library',
                            clean(section.lower()) + ('s' if not section.endswith('s') else '') + '.py')
    with codecs.open(parts_py, 'w', encoding='utf-8') as generated_file:
        generated_file.write(part_str)

if not os.path.exists(parts_json):
    parts = list(get_parts())
    with open(parts_json, 'w') as parts_json_file:
        json.dump(parts, parts_json_file, cls=JsonEncoder, indent=4)
else:
    parts = json.load(open(parts_json, 'r'), cls=JsonDecoder)

__init__ = os.path.join('ldraw', 'library', '__init__.py')
open(__init__, 'w').close()

pass
