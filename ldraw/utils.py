"""
Some utils functions
"""

import collections
import re
import os
from distutils.util import strtobool
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def clean(input_string):
    """
    Cleans a description string:

    :param input_string:
    :return:
    """
    input_string = re.sub(r"\W+", "_", input_string)
    input_string = re.sub(r"_x_", "x", input_string)
    return input_string


def camel(input_string):
    """ Returns a CamelCase string """
    return "".join(x for x in input_string.title() if not x.isspace())


def prompt(query):
    print("%s [y/n]: " % query)
    while True:
        val = input()
        try:
            return strtobool(val)
        except ValueError:
            print("Please answer with y/n")


def ensure_exists(path):
    """ makes the directory if it does not exist"""
    os.makedirs(path, exist_ok=True)
    return path


# https://stackoverflow.com/a/6027615
def flatten(input_dict, parent_key='', sep='.'):
    """ flatten a dictionary """
    items = []
    for key, value in input_dict.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


# https://stackoverflow.com/a/6027615
def flatten2(input_dict, parent_key=None):
    """ flatten a dictionary """
    items = []
    for key, value in input_dict.items():
        new_key = parent_key + (key,) if parent_key is not None else (key, )
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten2(value, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def file_exists(location):
    request = Request(location)
    request.get_method = lambda: "HEAD"
    try:
        response = urlopen(request)
        return True
    except HTTPError:
        return False


def _path_insensitive(path):
    # https://stackoverflow.com/a/8462613/1685379
    """
    Recursive part of path_insensitive to do the work.
    """

    if path == '' or os.path.exists(path):
        return path

    base = os.path.basename(path)  # may be a directory or a file
    dirname = os.path.dirname(path)

    suffix = ''
    if not base:  # dir ends with a slash?
        if len(dirname) < len(path):
            suffix = path[:len(path) - len(dirname)]

        base = os.path.basename(dirname)
        dirname = os.path.dirname(dirname)

    if not os.path.exists(dirname):
        dirname = _path_insensitive(dirname)
        if not dirname:
            return

    # at this point, the directory exists but not the file

    try:  # we are expecting dirname to be a directory, but it could be a file
        files = os.listdir(dirname)
    except OSError:
        return

    baselow = base.lower()
    try:
        basefinal = next(fl for fl in files if fl.lower() == baselow)
    except StopIteration:
        return

    if basefinal:
        return os.path.join(dirname, basefinal) + suffix
    else:
        return


def path_insensitive(path):
    return _path_insensitive(path) or path
