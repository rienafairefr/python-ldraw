""" compatibility module for python 2/3 """
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
