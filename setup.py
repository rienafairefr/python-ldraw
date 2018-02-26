#! /usr/bin/env python
# coding=utf-8

from distutils.core import setup

from setuptools import find_packages

import ldraw

setup(
    name="pyldraw",
    description="A package for working with LDraw format files.",
    long_description=open('README.rst').read(),
    author=" David Boddie <david@boddie.org.uk>",
    maintainer="Matthieu Berthomé <rienafairefr@gmail.com>",
    author_email="rienairefr@gmail.com, david@boddie.org.uk",
    version=ldraw.__version__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ldr2inv = ldraw.tools.ldr2inv:main',
            'ldr2png = ldraw.tools.ldr2png:main',
            'ldr2pov = ldraw.tools.ldr2pov:main',
            'ldr2svg = ldraw.tools.ldr2svg:main',
        ],
    },
    install_requires=['numpy']
)
