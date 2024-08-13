#!/bin/env python3

import sys
import os

#safe pymetranet import
try:
    import pymetranet
except ModuleNotFoundError as ex:
    #exe_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    exe_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    if os.path.isfile(exe_dir):
        #detected exe_dir as file instead of dir, use parent dir, this occurs when
        #running a python program from a self-executable zip file generated with zipapps
        exe_dir = os.path.dirname(exe_dir)
    paths = [os.path.abspath(os.path.join(exe_dir, "pymetranet")),
        os.path.abspath(os.path.join(exe_dir, "..", "pymetranet")),
        os.path.abspath(os.path.join(exe_dir, "..", "lib", "pymetranet")),
        os.path.abspath(os.path.join(exe_dir, "..", "..", "..", "share", "src", "pymetranet", "pymetranet")),
        os.path.abspath(os.path.join(exe_dir, "..", "..", "..", "..", "share", "src", "pymetranet", "pymetranet")),
        os.path.abspath(os.path.join(exe_dir, "..", "..", "..", "..", "..", "share", "src", "pymetranet", "pymetranet"))]
    found = False
    
    #search library in zip format
    for path in paths:
        zip_file = path + ".pyz"
        #searching for 'zip_file' file
        if os.path.isfile(zip_file):
            found = True
            #found pymetranet as zip file 'zip_file', add it to sys path
            sys.path.append(zip_file)
            break
    
    if not found:
        #search library as folder
        for path in paths:
            #searching for dir 'path'
            if os.path.isdir(path):
                found = True
                #found pymetranet as dir in 'path', add dir parent to sys path
                sys.path.append(os.path.dirname(path))
                break
    if not found:
        raise ModuleNotFoundError("can't find pymetranet package not in the system nor in known local relative paths")