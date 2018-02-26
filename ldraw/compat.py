""" compatibility module for python 2/3 """
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    from urllib import urlretrieve
    from StringIO import StringIO

    do_execfile = execfile
else:
    from io import StringIO
    from urllib.request import urlretrieve

    def do_execfile(script, global_vars, local_vars):
        with open("somefile.py") as f:
            code = compile(f.read(), "somefile.py", 'exec')
            exec(code, global_vars, local_vars)