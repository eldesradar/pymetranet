#!/bin/env python3

#import from system
import sys
import os
import math
import argparse
import time
import numpy as np

#safe pymetranet import
import import_pymetranet
from pymetranet import ProductFile, Linker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", type=str, default="default")
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    
    for file_name in args.infile:
        #load product file
        print("loading product %s..." % file_name)
        prod = ProductFile()
        prod.load_file(file_name)
        print("product file %s successfully loaded!" % file_name)

        #show header info
        infos = prod.get_header_info()
        for i in range(len(infos)):
            print("info[%d/%d]:" % (i+1, len(infos)), infos[i])

        #generate links for the file read
        print("generating hard links for for '%s' link file: '%s'" % (file_name, args.link))
        Linker.create_links(file_name, args.link)

    return 0

if __name__ == '__main__':
    main()
