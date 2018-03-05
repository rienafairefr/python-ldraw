import json

import collections
import re

import os

from ldraw.colour import Colour
from ldraw.geometry import Vector, Matrix
from ldraw.lines import *
from ldraw.pieces import Piece

record_types = [Comment,
                MetaCommand,
                Line,
                Triangle,
                Quadrilateral,
                OptionalLine, Vector, Matrix, Piece]

enum_types = [Colour]

record_types_dict = {t.__name__: t for t in record_types}
enum_types_dict = {t.__name__: t for t in enum_types}


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Part):
            return {'__type': 'Part', 'objects': obj.objects}

        for x in record_types:
            if isinstance(obj, x):
                returnvalue = {'__record_type': x.__name__}
                returnvalue.update(obj.__dict__)
                return returnvalue

        for y in enum_types:
            if isinstance(obj, y):
                return {'__enum': str(obj)}

        return json.JSONEncoder.default(self, obj)


class JsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '__type' not in obj:
            return obj
        type = obj['__type']
        if type == 'Part':
            returnvalue = Part()
            returnvalue.objects = obj['objects']
            return returnvalue
        if '__record_type' in obj:
            kwargs = {k: v for k, v in obj.items() if not k.startswith('__')}
            return record_types_dict[obj['__record_type']](**kwargs)
        if '__enum' in obj:
            name, member = obj["__enum"].split(".")
            return getattr(enum_types_dict[name], member)


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def clean(varStr):
    varStr = re.sub('\W|^(?=\d)', '_', varStr)
    varStr = re.sub('\_+', '_', varStr)
    varStr = re.sub('_x_', 'x', varStr)
    return varStr


def camel(input):
    return ''.join(x for x in input.title() if not x.isspace())


def ensure_exists(path):
    try:
        os.makedirs(path)
    except:
        pass
    return path


# https://stackoverflow.com/a/6037657
def unflatten(dictionary, sep='.'):
    result_dict = {}
    for key, value in dictionary.iteritems():
        parts = key.split(sep)
        new_dict = result_dict
        for part in parts[:-1]:
            if part not in new_dict:
                new_dict[part] = {}
            new_dict = new_dict[part]
        new_dict[parts[-1]] = value
    return result_dict


# https://stackoverflow.com/a/6027615
def flatten(input_dict, parent_key='', sep='.'):
    items = []
    for key, value in input_dict.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)