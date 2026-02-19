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

        #detect if product contains 8bit unsigned integer data or 32bit float data
        is_8bit_uint: bool = prod.is_8bit_uint()
        is_32bit_float: bool = prod.is_32bit_float()
        if not is_8bit_uint and not is_32bit_float:
            print("unable to detect data type of product %s, skipping it!" % file_name)
            continue

        #if the product is 8bit unsigned integer, get the conversion table and print it
        conv_table = prod.get_conv_table()
        if conv_table is not None:
            for i in range(conv_table.size):
                print("table[%d]:" % i, conv_table[i])
        else:
            print("no conversion table found")

        #coerence check: if the product is 8bit unsigned integer, conv_table can't be None
        if is_8bit_uint and conv_table is None:
            print("product is 8bit unsigned integer but no conversion table found!")
            continue

        #get data and reference only values different from zero
        prod_data = prod.data
        buffer = prod_data.data
        assert buffer.ndim == 2

        #iterate over product data using zip
        iterate_with_zip: bool = True
        if iterate_with_zip:
            indices = zip(*np.where(buffer != 0)) if is_8bit_uint else zip(*np.where(~np.isnan(buffer)))
            print("iterate on indices ...")
            (print_8bit_uint_values_indices(buffer, indices, conv_table)
                if is_8bit_uint
                else print_32bit_float_values_indices(buffer, indices))
            #this is to demonstrate that once indices is consumed
            #it it no more usable a second time whereas it is a generator
            #which cerates a consumable iterator. you can't use indices
            #after you have consumed it the firt time
            print("trying to iterate again on indices ...")
            (print_8bit_uint_values_indices(buffer, indices, conv_table)
                if is_8bit_uint
                else print_32bit_float_values_indices(buffer, indices))

        #iterate over product data NOT using zip
        iterate_filter: bool = True
        if iterate_filter:
            filter = np.where(buffer != 0) if is_8bit_uint else np.where(~np.isnan(buffer))
            assert len(filter) == buffer.ndim
            idx_rows = filter[0]
            idx_cols = filter[1]
            assert len(idx_rows) == len(idx_rows)
            print("iterate on idx_rows and idx_cols ...")
            (print_8bit_uint_values_rows_cols(idx_rows, idx_cols, buffer, conv_table)
                if is_8bit_uint
                else print_32bit_float_values_rows_cols(idx_rows, idx_cols, buffer, conv_table))
            #this is to demonstrate that yuo can consume idx_rows and idx_cols
            #all the times you want
            print("trying to iterate again on idx_rows and idx_cols ...")
            (print_8bit_uint_values_rows_cols(idx_rows, idx_cols, buffer, conv_table)
                if is_8bit_uint
                else print_32bit_float_values_rows_cols(idx_rows, idx_cols, buffer, conv_table))

    return 0

def print_8bit_uint_values_indices(buffer, indices, conv_table):
    for i, j in indices:
        print("data[%d,%d] - DN:" % (i, j), buffer[i, j],
            "converted value:", conv_table[buffer[i, j]])

def print_8bit_uint_values_rows_cols(idx_rows, idx_cols, buffer, conv_table):
    for i in range(len(idx_rows)):
        print("data[%d,%d] - DN:" % (idx_rows[i], idx_cols[i]), buffer[idx_rows[i], idx_cols[i]],
            "converted value:", conv_table[buffer[idx_rows[i], idx_cols[i]]])

def print_32bit_float_values_rows_cols(idx_rows, idx_cols, buffer, conv_table):
    for i in range(len(idx_rows)):
        print("data[%d,%d]:" % (idx_rows[i], idx_cols[i]), buffer[idx_rows[i], idx_cols[i]])

def print_32bit_float_values_indices(buffer, indices):
    for i, j in indices:
        print("data[%d,%d]:" % (i, j), buffer[i, j])

if __name__ == '__main__':
    main()
