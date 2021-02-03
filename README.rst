.. image:: https://coveralls.io/repos/github/rienafairefr/python-ldraw/badge.svg?branch=master
    :target: https://coveralls.io/github/rienafairefr/python-ldraw?branch=master

.. image:: https://github.com/rienafairefr/python-ldraw/workflows/Python%20package/badge.svg
    :target: https://github.com/rienafairefr/python-ldraw/actions?query=workflow%3A%22Python+package%22

.. image:: https://img.shields.io/pypi/pyversions/pyldraw.svg   :alt: PyPI - Python Version
    :target: https://pypi.python.org/pypi/pyldraw


======================
pyldraw Python Package
======================

:Author: `rienafairefr`_ code originally from `David Boddie`_

.. contents::


Introduction
------------

LDraw_ is a standard format used by CAD applications that create LEGO models
and scenes. 

The ``pyldraw`` package provides facilities to allow users to create LDraw scene
descriptions using the Python_ programming language. Pieces are specified by
their positions, orientations and other properties in normal executable Python
scripts which are run to create model files.

The ``pyldraw`` package includes code to have the complete LDraw library available
to you through normal Python imports, like::

  from ldraw.library.colours import Light_Grey
  from ldraw.library.parts.minifig.accessories import Seat2X2
  from ldraw.library.parts.bricks import Brick1X2WithClassicSpaceLogoPattern
  # or
  from ldraw.library.parts import Brick1X2WithClassicSpaceLogoPattern

The actual parts library hierarchy (in which subpackage each brick is, etc...),
is still a work in progress. You can always specify parts by their LDraw code::

  rover = group()
  Piece(Light_Grey, Vector(-10, -32, -90),
            Identity(), "3957a", rover)


Compatibility
-------------

This is tested on Python 2.7, and 3.4+

Installation
------------

The simplest way is through pip::

  pip install pyldraw


Auto-generation of the ldraw.library.* package
----------------------------------------------

The ldraw.library.* package is kind of special, it is generated from a LDraw parts library
with the parts.lst itself auto-generated using pymklist_.

Before running code that needs something in the ldraw.library, it is recommend to
* download a parts library
This is done through the CLI: `ldraw download`
You can select a given, down to the first LDRAW version (beta 0.27, almost from last century), though it's not sure how compatible it
is with pyldraw. Use `--version 2020-01` to have the parts library for update 2020-01
If you've downloaded multiple versions, use `ldraw use` to select which one you want to use
* generate the ldraw.library package
Use `ldraw generate`

Afterwards, when running code that needs something in the ldraw.library, pyldraw will know (through a ``sys.meta_path`` hook)
and use the generated code. It also attempts to auto-generate it on-the-fly.

Considering that the toolchain download, generation, python code generation takes
quite some time, and we don't want to re-download anyway,
the generated library is locally written, and reused on subsequent import or python scripts run.

If you change version or modify it (e.g., adding unofficial partsà, the library should be re-generated (either manually
or on-the-fly).

The cached generated library is stored in an OS-dependent cache directory (somewhere in ``~/.local`` for Linux)

Examples
--------

A number of examples are provided in the ``examples`` directory. When run, each
of these will write model information to stdout/console. To create a model file
from an example, redirect its output to a file.


Part Descriptions
-----------------

Even though this package does include a list of parts derived from those supplied in
the official LDraw archive, users can download or modify this
list separately. The ldraw.library.* hierarchy will stay current with the LDraw database
setup in the configuration

Parts are available from the ldraw.library namespace as described above, but you can also use the Parts class::

  from ldraw.parts import Parts
  parts = Parts("parts.lst") # provide your custom parts.lst path

Parts can then be accessed using the relevant dictionary
attributes of the ``parts`` instance. For example::

  cowboy_hat = parts.minifig.hats["Hat Cowboy"]
  head = parts.minifig.heads["Head with Solid Stud"]
  brick1x1 = parts.others["Brick  1 x  1"]

Writers and Tools
-----------------

The ``ldraw.writers`` package aims to provide a set of classes that write out
LDraw descriptions in other file formats. Currently, it contains the ``povray``
module which provides a class for writing out LDraw descriptions as POV-Ray
scenes.

The ``ldr2pov`` tool, uses the ``povray`` module to allow LDraw (``.ldr``) files
to be conveniently converted to POV-Ray (``.pov``) scene files.
Note that, since the LDraw format does not include
information about camera locations, it is necessary to pass this information
on the command line.

For example, on a GNU/Linux system, we can execute command lines like these
to take the ``figures.py`` example file, create an LDraw model file (``temp.ldr``),
and convert that to a POV-Ray scene file (``temp.pov``)::

  python examples/figures.py > temp.ldr
  ldr2pov models/figures.ldr temp.pov 160.0,80.0,-240.0
  povray +Itemp.pov +FN16 +Otemp.png +Q6

Finally, POV-Ray is used to process the scene description and create a PNG
image file (``temp.png``).

Some other tools and writers are included,

  - ldr2inv:

  Transforms a LDR file into a file containing the Bill Of Materials or Inventory of the model

  - ldr2png

  Renders the LDR file into a PNG file

  - ldr2svg

  Renders the LDR file into a vector image in SVG


License
-------

The contents of this package are licensed under the GNU General Public License
(version 3 or later)::

 pyldraw, a Python package for creating LDraw format files.
 Copyright (C) 2008 David Boddie <david@boddie.org.uk>

 Some parts Copyright (C) 2021 Matthieu Berthomé <matthieu@mmea.fr>

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


Trademarks
----------

LDraw is a trademark of the Estate of James Jessiman. LEGO is a registered
trademark of the LEGO Group.

Origins
-------

This repo was extracted from the mercurial repository at
https://anonscm.debian.org/hg/python-ldraw/main

It will not try to stay updated with the upstream repo of the original author, David Boddie,
The goal is to see what might be done, the original repo hasn't been updated since 2011


.. _LDraw:          http://www.ldraw.org/
.. _Python:         http://www.python.org/
.. _pymklist:       https://github.com/rienafairefr/pymklist
.. _`David Boddie`: mailto:david@boddie.org.uk
.. _`rienafairefr`: mailto:matthieu@mmea.fr
