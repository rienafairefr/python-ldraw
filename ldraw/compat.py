""" compatibility module for python 2/3 """
# pylint: disable=unused-import
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
