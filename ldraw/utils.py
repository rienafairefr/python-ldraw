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
