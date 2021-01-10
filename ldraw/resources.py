import codecs

import pkg_resources


def get_resource(filename):
    return pkg_resources.resource_filename("ldraw", filename)


def get_resource_content(filename):
    return codecs.open(get_resource(filename), "r", encoding="utf-8").read()
