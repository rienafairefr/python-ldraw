.. image:: https://coveralls.io/repos/github/rienafairefr/python-ldraw/badge.svg?branch=master
:target: https://coveralls.io/github/rienafairefr/python-ldraw?branch=master
.. image:: https://travis-ci.org/rienafairefr/python-ldraw.svg?branch=master
    :target: https://travis-ci.org/rienafairefr/python-ldraw



======================
pyldraw Python Package
======================

:Author: `Matthieu Berthomé, code originally from David Boddie`_
:Date: 2018-02-22
:Version: 0.3

.. contents::


Introduction
------------

LDraw_ is a standard format used by CAD applications that create LEGO models
and scenes. 

The `pyldraw` package provides facilities to allow users to create LDraw scene
descriptions using the Python_ programming language. Pieces are specified by
their positions, orientations and other properties in normal executable Python
scripts which are run to create model files.

The `pyldraw` packages as deployed on PyPi includes code to have the complete LDraw library available
to you through normal Python imports, like::

  from ldraw.library.colours import Light_Grey
  from ldraw.library.parts.minifig.accessories import Seat2X2
  from ldraw.library.parts.others import Brick1X2WithClassicSpaceLogoPattern

The actual parts library hierarchy is still a work in progress. You can always specify parts
by their LDraw code::

  rover = group()
  Piece(Light_Grey, Vector(-10, -32, -90),
            Identity(), "3957a", rover)


When installing from the git repository,

Compatibility
-------------

Be warned that some parts of the library (only some ldr2*** tools) require a working PyQt4/SIP installation, and for now
have only been tested on Python 2.7.

The other parts seem to work fine on Python 3.4+

Installation
------------

The simplest way is through pip::

  pip install pyldraw

If you download the source code, if you want to use the ldraw.library.* hierarchy,
you must download the LDraw library and generate the python code before running the installer (`python setup.py install`)
To do that, install the requirements for code generation `pip install -r gen-requirements.txt`, then run::

  python -m ldraw.download
  python -m ldraw.library_gen

This will generate the `ldraw.library` package, then you can install pyldraw with::

  python setup.py install


You may need to become the root user or administrator to do this. Code generation shouldn't need root it's using
your user data dir (through the `appdirs` package's user_data_dir)


Examples
--------

A number of examples are provided in the `examples` directory. When run, each
of these will write model information to the console. To create a model file
from an example, redirect its output to a file.


Part Descriptions
-----------------

Even though this package does include a list of parts derived from those supplied in
the official LDraw archive, users can download or modify this
list separately. The ldraw.library.* hierarchy will stay current with the LDraw database
at the moment the package was deployed on Pypi though

It is possible to use the `ldraw.parts` module to create a parts database from within a scene
script in the following way::

  from ldraw.parts import Parts
  parts = Parts("parts.lst") # provide your custom parts.lst path

Parts can then be accessed using the relevant dictionary
attributes of the `parts` instance. For example::

  cowboy_hat = parts.minifig.hats["Hat Cowboy"]
  head = parts.minifig.heads["Head with Solid Stud"]
  brick1x1 = parts.others["Brick  1 x  1"]

Writers and Tools
-----------------

The `ldraw.writers` package aims to provide a set of classes that write out
LDraw descriptions in other file formats. Currently, it contains the `povray`
module which provides a class for writing out LDraw descriptions as POV-Ray
scenes.

The `ldr2pov` tool, uses the `povray` module to allow LDraw (`.ldr`) files
to be conveniently converted to POV-Ray (`.pov`) scene files.
Note that, since the LDraw format does not include
information about camera locations, it is necessary to pass this information
on the command line.

For example, on a GNU/Linux system, we can execute command lines like these
to take the `figures.py` example file, create an LDraw model file (`temp.ldr`),
and convert that to a POV-Ray scene file (`temp.pov`)::

  python examples/figures.py > temp.ldr
  ldr2pov /path/to/parts.lst models/figures.ldr temp.pov 160.0,80.0,-240.0
  povray +Itemp.pov +FN16 +Otemp.png +Q6

Finally, POV-Ray is used to process the scene description and create a PNG
image file (`temp.png`).

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

 ldraw, a Python package for creating LDraw format files.
 Copyright (C) 2008 David Boddie <david@boddie.org.uk>

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

It will not try to stay updated with the upstream repo of the original author, David Boddie
The goal is to see what might be done, the original repo hasn't been updated since 2011

Some of the documentation underneath might be outdated
with the current state of the repo until the API congeals, sorry about that


.. _LDraw:          http://www.ldraw.org/
.. _Python:         http://www.python.org/
.. _`David Boddie`: mailto:david@boddie.org.uk
