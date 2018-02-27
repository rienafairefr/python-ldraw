#!/usr/bin/env python
import codecs
import json
import random
import re
import shutil
from urllib import urlretrieve
import zipfile
import os

from ldraw.parts import Parts, CONTAINERS
import pystache

from ldraw.utils import JsonEncoder, JsonDecoder

url = 'http://www.ldraw.org/library/updates/complete.zip'

retrieved = "complete.zip"

if not os.path.exists(retrieved):
    print('retrieve the complete.zip from ldraw.org ...')
    urlretrieve(url, filename=retrieved)

if not os.path.exists('tmp/ldraw'):
    print('unzipping the complete.zip ...')
    zip_ref = zipfile.ZipFile(retrieved, 'r')
    zip_ref.extractall('tmp')
    zip_ref.close()

if not os.path.exists('tmp/mklist/mklist'):
    print('unzipping the mklist  zip ...')
    zip_ref = zipfile.ZipFile('tmp/ldraw/mklist1_6.zip', 'r')
    zip_ref.extractall('tmp/mklist')
    zip_ref.close()

    print('patch the mklist  sources ...')
    patch = """diff -Naur mklist.orig/makefile mklist/makefile
--- mklist.orig/makefile	2018-02-23 10:05:40.000000000 +0100
+++ mklist/makefile	2018-02-23 10:05:47.111079214 +0100
@@ -1,6 +1,6 @@
 CC=gcc

-CFLAGS= -I./include
+CFLAGS= -I./include -D MAX_PATH=256

 AR = ar
 RANLIB = ranlib
diff -Naur mklist.orig/mklist.c mklist/mklist.c
--- mklist.orig/mklist.c	2018-02-23 10:05:06.000000000 +0100
+++ mklist/mklist.c	2018-02-23 10:05:12.602915933 +0100
@@ -84,7 +84,7 @@
 int GetShortPathName(char *longpath, char * shortpath, int psize)
 {
     strncpy(shortpath, longpath, psize);
-    return(strlen(shortpath);
+    return(strlen(shortpath));
 }
 #endif
"""
    open('tmp/mklist.patch', 'w').write(patch)

    os.system('dos2unix tmp/mklist/mklist.c')
    os.system('dos2unix tmp/mklist/makefile')
    os.system('patch -d tmp -l -p0 < tmp/mklist.patch')
    os.system('make -C tmp/mklist')

if not os.path.exists('tmp/ldraw/parts.lst'):
    print('mklist ...')
    os.system('tmp/mklist/mklist -d -i tmp/ldraw/parts -o tmp/ldraw/parts.lst')

p = Parts('tmp/ldraw/parts.lst')

parts_template = codecs.open(os.path.join('templates', 'metaparts.mustache'), 'r', encoding='utf-8').read()
template = pystache.parse(parts_template)


def clean(varStr):
    varStr = re.sub('\W|^(?=\d)', '_', varStr)
    varStr = re.sub('\_+', '_', varStr)
    varStr = re.sub('_x_', 'x', varStr)
    return varStr


def camel(input):
    return ''.join(x for x in input.title() if not x.isspace())


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

sections += (('others', p.Others), )

for section, parts in sections:
    parts_list = [get_part_dict(description) for description in parts]
    parts_list = sorted(parts_list, key=lambda o: o['description'])
    part_str = pystache.render(template, context={'containers': CONTAINERS,
                                                  'parts': parts_list})
    parts_py = os.path.join('ldraw', 'library', clean(section.lower()) + ('s' if not section.endswith('s') else '') + '.py')
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
