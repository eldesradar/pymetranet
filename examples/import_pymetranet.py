#!/bin/env python

import sys
import os
import inspect

def find_local_pymetranet(path):
    if os.path.isdir(path):
        return True
        
    return False

#safe pymetranet import
try:
    from pymetranet import *
except ModuleNotFoundError as ex:
    script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    paths = [os.path.abspath(os.path.join(script_dir, "..", "pymetranet")),
        os.path.abspath(os.path.join(script_dir, "..", "lib", "pymetranet")),
        os.path.abspath(os.path.join(script_dir, "..", "..", "..", "..", "..", "share", "src", "pymetranet")),
        os.path.abspath(os.path.join(script_dir, "..", "..", "..", "share", "src", "pymetranet"))]
    found = False
    for path in paths:
        if find_local_pymetranet(path):
            found = True
            sys.path.insert(0, os.path.dirname(path))
            break
    if not found:
        raise ModuleNotFoundError("can't find pymetranet package not in the system nor in known local relative paths")