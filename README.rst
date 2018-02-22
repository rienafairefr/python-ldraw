This repo is a git copy of the repository at
https://anonscm.debian.org/hg/python-ldraw/main

It will not try to stay updated with the upstream repo of the original author, David Boddie
The goal is to see what might be done, the original repo hasn't been updated since 2011

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

The `ldraw` package provides facilities to allow users to create LDraw scene
descriptions using the Python_ programming language. Pieces are specified by
their positions, orientations and other properties in normal executable Python
scripts which are run to create model files.


Installation
------------

To install the package alongside other packages and modules in your Python
installation, unpack the contents of the archive. At the command line, enter
the directory containing the ``setup.py`` script and install it by typing the
following::

  python setup.py install

You may need to become the root user or administrator to do this.


Examples
--------

A number of examples are provided in the `examples` directory. When run, each
of these will write model information to the console. To create a model file
from an example, redirect its output to a file.


Part Descriptions
-----------------

This package does not include a list of parts derived from those supplied in
the official LDraw archive, so users will have to download and consult this
list separately. However, once the user has obtained this file, it is possible
to use the `ldraw.parts` module to create a parts database from within a scene
script in the following way::

  from ldraw.parts import Parts
  parts = Parts("parts.lst") # parts.lst is supplied with LDraw

Figure-specific parts can then be accessed using the relevant dictionary
attributes of the `parts` instance. For example::

  cowboy_hat = parts.Hats["Hat Cowboy"]
  head = parts.Heads["Head with Solid Stud"]

Although this makes it easier to refer to parts, you can still refer to them
using their part numbers. For example::

  figure = Person()
  print figure.head(Yellow, 35)
  print figure.hat(Black, "3901")  # Hair Male

This can be useful if you want to refer unambiguously to a specific part.


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



.. _LDraw:          http://www.ldraw.org/
.. _Python:         http://www.python.org/
.. _`David Boddie`: mailto:david@boddie.org.uk
