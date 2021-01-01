"""
Some utils functions
"""

import collections
import logging
import re
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def clean(input_string):
    """
    Cleans a description string:

    :param input_string:
    :return:
    """
    input_string = re.sub(r'\W+', '_', input_string)
    input_string = re.sub(r'_x_', 'x', input_string)
    return input_string


def camel(input_string):
    """ Returns a CamelCase string """
    return ''.join(x for x in input_string.title() if not x.isspace())


def ensure_exists(path):
    """ makes the directory if it does not exist"""
    try:
        print(f"ensure_exists {path}")
        os.makedirs(path)
    except OSError:
        pass
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


def file_exists(location):
    request = Request(location)
    request.get_method = lambda : 'HEAD'
    try:
        response = urlopen(request)
        return True
    except HTTPError:
        return False