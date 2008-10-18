#! /usr/bin/env python

from distutils.core import setup

import ldraw

setup(
    name         = "ldraw",
    description  = "A package for creating LDraw format files.",
    author       = "David Boddie",
    author_email = "david@boddie.org.uk",
    url          = "http://www.boddie.org.uk/david/Projects/Python/ldraw/",
    version      = ldraw.__version__,
    packages     = ["ldraw"]
    )
