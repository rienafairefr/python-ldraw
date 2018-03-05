#!/usr/bin/env python

"""
ldr2inv.py - Create parts lists from LDraw models.

Copyright (C) 2012 David Boddie <david@boddie.org.uk>

This file is part of the ldraw Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import codecs
import sys
import argparse

from ldraw.config import get_config
from ldraw.parts import Part, Parts, PartError
from ldraw.lines import Comment
from ldraw.pieces import Piece


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ldraw_file')
    parser.add_argument('output')

    args = parser.parse_args()

    ldr2inv(args.ldraw_file, args.output)


def ldr2inv(ldraw_path, inventory_path):
    config = get_config()
    parts = Parts(config['parts.lst'])

    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)

    inventory = {}
    length = 0

    for obj in model.objects:
        if not isinstance(obj, Piece):
            continue

        name = ""
        subpart = parts.part(code=obj.part)
        if subpart:
            for component in subpart.objects:
                if isinstance(component, Comment):
                    name = component.text
                    break
            else:
                sys.stderr.write("No name information for part: %s\n" % obj.text)

            inventory[name] = inventory.get(name, 0) + 1
            length = max(len(name), length)

    length += (4 - (length % 4))

    try:
        with codecs.open(inventory_path, 'w', encoding='utf-8') as f:
            items = inventory.items()
            items.sort()

            for name, number in items:
                padding = " " * (length - len(name))
                f.write("%s%s%i\n" % (name, padding, number))

    except IOError:
        sys.stderr.write("Failed to write inventory file: %s\n" % inventory_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
