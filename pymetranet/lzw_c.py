#!/bin/env python3

import ctypes
from ctypes import POINTER, c_int, c_ubyte
import numpy as np

def lzw_expand(zip_buffer, zip_size, unzip_size):
    """
    Decompresses data using the LZW algorithm via a C library.

    This function loads the 'libpymetranet.so' C library and calls its 'Expand' function to decompress
    a given compressed buffer. The decompressed output size is expected to match 'unzip_size'.

    Args:
        zip_buffer (np.ndarray): A NumPy array of type uint8 containing the compressed data.
        zip_size (int): The size (in bytes) of the compressed data.
        unzip_size (int): The expected size (in bytes) of the decompressed data.

    Returns:
        np.ndarray: A NumPy array of type uint8 containing the decompressed data.

    Raises:
        RuntimeError: If the decompression fails (i.e. the return value from the C function is <= 0).
    """
    #load the C library
    lib = ctypes.CDLL('./libpymetranet.so')

    #define the C function prototype for Expand
    lib.Expand.argtypes = [POINTER(c_ubyte), c_int, POINTER(c_ubyte), c_int]
    lib.Expand.restype = c_int

    #preallocate the output buffer for decompression
    expand_output_size = unzip_size  #expected decompressed size should be equals to the original one
    expand_output_buffer = np.zeros(expand_output_size, dtype=np.uint8)

    #call the C function Expand
    expand_input_ptr = zip_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    expand_output_ptr = expand_output_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    expand_result = lib.Expand(expand_input_ptr, zip_size, expand_output_ptr, expand_output_size)

    if expand_result <= 0:
        raise RuntimeError("error decompressing data (lzw_expand)")
    
    assert expand_result == unzip_size

    return expand_output_buffer

def lzw_compress(buffer, buffer_size):
    """
    Compresses data using the LZW algorithm via a C library.

    This function loads the 'libpymetranet.so' C library and calls its 'Compress' function to compress
    a given input buffer. The output buffer is preallocated to the size of the uncompressed data, and
    the function returns the portion of the buffer that contains the compressed data.

    Args:
        buffer (np.ndarray): A NumPy array of type uint8 containing the uncompressed data.
        buffer_size (int): The size (in bytes) of the uncompressed data.

    Returns:
        np.ndarray: A NumPy array of type uint8 containing the compressed data (sliced to the compressed size).

    Raises:
        RuntimeError: If the compression fails (i.e. the return value from the C function is <= 0).
    """
    #load the C library
    lib = ctypes.CDLL('./libpymetranet.so')

    #define the C function prototype for Compress
    lib.Compress.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
    lib.Compress.restype = ctypes.c_int

    #preallocate the output buffer for compression (same size as uncompressed data to be sure)
    zip_buffer = np.zeros(buffer_size, dtype=np.uint8)

    #call the C function Compress
    input_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    output_ptr = zip_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    compressed_size = lib.Compress(input_ptr, buffer_size, output_ptr, buffer_size)
    
    if compressed_size <= 0:
        raise RuntimeError("error compressing data (lzw_compress)")
    
    return zip_buffer[:compressed_size]
