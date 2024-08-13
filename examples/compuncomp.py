#!/bin/env python3

#import from system
import sys
import os
import math
import argparse
import time
import numpy as np
from PIL import Image, ImageDraw

#safe pymetranet import
import import_pymetranet
from pymetranet import ProductFile, lzw15_compress, lzw15_decompress

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

        #iterate over product data
        buffer_from_load_file = prod.data.data
        filter = np.where(buffer_from_load_file >= 0)
        idx_rows = filter[0]
        idx_cols = filter[1]

        #compress data, uncompress again
        buffer_of_bytes_from_loaded_file = buffer_from_load_file.tobytes()
        print("len of buffer_of_bytes_from_loaded_file:", len(buffer_of_bytes_from_loaded_file))
        compressed = lzw15_compress(buffer_of_bytes_from_loaded_file)
        compressed_bytes = b"".join(compressed)
        print("len of compressed_bytes:", len(compressed_bytes))
        #newbytes = b"".join(lzw15_decompress(compressed))
        newbytes = b"".join(lzw15_decompress(compressed_bytes))
        print("len of newbytes:", len(newbytes))
        oldbytes = buffer_from_load_file.tobytes()
        print("len of oldbytes:", len(oldbytes))
        print("oldbytes == newbytes:", oldbytes == newbytes)

        #match data (they must be equal)
        for i in range(len(idx_rows)):
            i_idx = idx_rows[i]
            j_idx = idx_cols[i]
            k_idx = i_idx * buffer_from_load_file.shape[0] + j_idx
            if buffer_from_load_file[i_idx, j_idx] != newbytes[k_idx]:
                print("buffer_from_load_file[%d,%d] different from newbytes[%d]:" % (i_idx, j_idx, k_idx),
                      buffer_from_load_file[i_idx, j_idx], newbytes[k_idx])
                print("oldbytes[%d]:" % k_idx, oldbytes[k_idx], "newbytes[%d]" % k_idx, newbytes[k_idx])
                break
            else:
                print("buffer_from_load_file[%d,%d] equals to newbytes[%d]:" % (i_idx, j_idx, k_idx),
                      buffer_from_load_file[i_idx, j_idx],
                      "buffer_of_bytes_from_loaded_file[%d]:" % k_idx, buffer_of_bytes_from_loaded_file[k_idx],
                      "newbytes[%d]:" % k_idx, newbytes[k_idx],
                      "oldbytes[%d]:" % k_idx, oldbytes[k_idx])

    return 0

if __name__ == '__main__':
    main()
