#!/bin/env python3

#import from system
import argparse
import numpy as np

#safe pymetranet import
import import_pymetranet
from pymetranet import ProductFile

def main():
    parser = argparse.ArgumentParser()
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

        #get data and reference only values different from zero
        prod_data = prod.data
        buffer = prod_data.data
        assert buffer.ndim == 2

        #iterate over product data using zip
        iterate_with_zip: bool = True
        if iterate_with_zip:
            indices = zip(*np.where(buffer != 0))
            print("iterate on indices ...")
            for i, j in indices:
                print("data[%d,%d]:" % (i, j), buffer[i, j])
            #this is to demonstrate that once indices is consumed
            #it it no more usable a second time whereas it is a generator
            #which cerates a consumable iterator. you can't use indices
            #after you have consumed it the firt time
            print("trying to iterate again on indices ...")
            for i, j in indices:
                print("data[%d,%d]:" % (i, j), buffer[i, j])

        #iterate over product data NOT using zip
        iterate_filter: bool = True
        if iterate_filter:
            filter = np.where(buffer != 0)
            assert len(filter) == buffer.ndim
            idx_rows = filter[0]
            idx_cols = filter[1]
            assert len(idx_rows) == len(idx_rows)
            print("iterate on idx_rows and idx_cols ...")
            for i in range(len(idx_rows)):
                print("data[%d,%d]:" % (idx_rows[i], idx_cols[i]), buffer[idx_rows[i], idx_cols[i]])
            #this is to demonstrate that yuo can consume idx_rows and idx_cols
            #all the times you want
            print("trying to iterate again on idx_rows and idx_cols ...")
            for i in range(len(idx_rows)):
                print("data[%d,%d]:" % (idx_rows[i], idx_cols[i]), buffer[idx_rows[i], idx_cols[i]])

    return 0

if __name__ == '__main__':
    main()
