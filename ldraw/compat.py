""" compatibility module for python 2/3 """


def do_execfile(script, global_vars, local_vars):
    with open(script) as f:
        code = compile(f.read(), script, 'exec')
        exec (code, global_vars, local_vars)
