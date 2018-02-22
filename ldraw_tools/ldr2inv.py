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

import sys
import argparse
from ldraw.parts import Comment, Part, Parts, PartError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ldraw_parts_file')
    parser.add_argument('ldraw_file')
    parser.add_argument('output')

    args = parser.parse_args()

    parts_path = args.ldraw_parts_file
    ldraw_path = args.ldraw_file
    inventory_path = args.output

    parts = Parts(parts_path)

    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)

    inventory = {}
    length = 0

    for obj in model.objects:

        if obj.part == "LIGHT":
            continue

        name = ""
        for component in parts.part(code=obj.part).objects:

            if isinstance(component, Comment):
                name = component.text
                break
        else:
            sys.stderr.write("No name information for part: %s\n" % obj.part)

        inventory[name] = inventory.get(name, 0) + 1
        length = max(len(name), length)

    length += (4 - (length % 4))

    try:
        f = open(inventory_path, "w")

        items = inventory.items()
        items.sort()

        for name, number in items:
            padding = " " * (length - len(name))
            f.write("%s%s%i\n" % (name, padding, number))

        f.close()

    except IOError:
        sys.stderr.write("Failed to write inventory file: %s\n" % inventory_path)
        sys.exit(1)

    sys.exit()


if __name__ == "__main__":
    main()
