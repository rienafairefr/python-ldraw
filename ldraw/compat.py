""" compatibility module for python 2/3 """
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    from urllib import urlretrieve
    from StringIO import StringIO
    from __builtin__ import reduce

    do_execfile = execfile
else:
    from io import StringIO
    from urllib.request import urlretrieve
    from functools import reduce

    def do_execfile(script, global_vars, local_vars):
        with open(script) as f:
            code = compile(f.read(), script, 'exec')
            exec(code, global_vars, local_vars)

