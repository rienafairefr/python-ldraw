====================
ldraw Python Package
====================

:Author: `David Boddie`_
:Date: 2008-07-13
:Version: 0.11

*Note: This text is marked up using reStructuredText formatting. It should be
readable in a text editor but can be processed to produce versions of this
document in other formats.*


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
