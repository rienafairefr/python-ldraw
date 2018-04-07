import pkg_resources


def get_resource(filename):
    return pkg_resources.resource_filename('ldraw', filename)