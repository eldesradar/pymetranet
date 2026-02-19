#!/bin/env python3

import os
import zipfile
import ctypes
from ctypes import POINTER, c_int, c_ubyte
import numpy as np

# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------
# The shared library libpymetranet.so can live in two different places
# depending on how pymetranet has been installed:
#
#   1. pip install  → libpymetranet.so is placed next to the .py files inside
#                     the package directory (e.g. site-packages/pymetranet/)
#
#   2. RPM install  → the package is shipped as pymetranet.pyz and
#                     libpymetranet.so sits next to it on the filesystem
#                     (e.g. /opt/metraserver/lib/)
#
# In case 2 the module is imported from inside a zip archive, so __file__
# contains a virtual path like /opt/metraserver/lib/pymetranet.pyz/pymetranet/lzw_c.py
# that does not correspond to a real directory. We therefore walk up the path
# until we either find the .so next to the .py files (case 1) or find the
# .pyz container and look for the .so beside it (case 2).

def _find_lib_path(lib_name: str = "libpymetranet.so") -> str:
    """
    Locates libpymetranet.so on the filesystem and returns its absolute path.

    Raises:
        RuntimeError: If the library cannot be found in any expected location.
    """
    module_file = os.path.abspath(__file__)

    # Walk up the directory tree starting from the module location.
    path = module_file
    while True:
        parent = os.path.dirname(path)
        if parent == path:
            # Reached the filesystem root without finding anything.
            break

        # Case 1: the .so is in the same real directory as the .py file.
        candidate = os.path.join(parent, lib_name)
        if os.path.isfile(candidate):
            return candidate

        # Case 2: the current segment is a .pyz archive; look beside it.
        if path.endswith(".pyz") or (os.path.isfile(path) and zipfile.is_zipfile(path)):
            candidate = os.path.join(parent, lib_name)
            if os.path.isfile(candidate):
                return candidate

        path = parent

    raise RuntimeError(
        f"Cannot find '{lib_name}'. "
        "Make sure the shared library is installed correctly alongside the pymetranet package."
    )

def _load_lib() -> ctypes.CDLL:
    """
    Loads libpymetranet.so and configures the argtypes/restype for every
    exported function used by this module.

    Returns:
        ctypes.CDLL: The loaded shared library with configured prototypes.
    """
    lib_path = _find_lib_path()
    lib = ctypes.CDLL(lib_path)

    # Expand(const unsigned char *in, int in_size, unsigned char *out, int out_size) -> int
    lib.Expand.argtypes = [POINTER(c_ubyte), c_int, POINTER(c_ubyte), c_int]
    lib.Expand.restype  = c_int

    # Compress(const unsigned char *in, int in_size, unsigned char *out, int out_size) -> int
    lib.Compress.argtypes = [POINTER(c_ubyte), c_int, POINTER(c_ubyte), c_int]
    lib.Compress.restype  = c_int

    return lib

# Load once at module import time; all functions in this module share this instance.
_lib = _load_lib()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def lzw_expand(zip_buffer: np.ndarray, zip_size: int, unzip_size: int) -> np.ndarray:
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
    #preallocate the output buffer for decompression
    expand_output_buffer = np.zeros(unzip_size, dtype=np.uint8)

    #prepare the pointers
    expand_input_ptr = zip_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    expand_output_ptr = expand_output_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

    #call the C function Expand
    expand_result = _lib.Expand(expand_input_ptr, zip_size, expand_output_ptr, unzip_size)

    if expand_result <= 0:
        raise RuntimeError("error decompressing data (lzw_expand)")
    
    assert expand_result == unzip_size

    return expand_output_buffer

def lzw_compress(buffer: np.ndarray, buffer_size: int) -> np.ndarray:
    """
    Compresses data using the LZW algorithm via a C library.

    This function loads the 'libpymetranet.so' C library and calls its 'Compress' function to compress
    a given input buffer. The output buffer is preallocated to the size of the uncompressed data, and
    the function returns the portion of the buffer that contains the compressed data.

    Args:
        buffer (np.ndarray): A NumPy array of type uint8 containing the uncompressed data.
        buffer_size (int): The size (in bytes) of the uncompressed data.

    Returns:
        np.ndarray: A NumPy array of type uint8 containing the compressed data
                    (sliced to the compressed size).

    Raises:
        RuntimeError: If the compression fails (i.e. the return value from the C function is <= 0).
    """
    # Pre-allocate the output buffer to the same size as the input; LZW can in
    # the worst case produce output larger than the input, but for the data sizes
    # encountered in practice this is a safe upper bound.
    zip_buffer = np.zeros(buffer_size, dtype=np.uint8)

    #prepare the pointers
    input_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    output_ptr = zip_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    
    #call the C function Compress
    compressed_size = _lib.Compress(input_ptr, buffer_size, output_ptr, buffer_size)
    
    if compressed_size <= 0:
        raise RuntimeError("error compressing data (lzw_compress)")
    
    return zip_buffer[:compressed_size]
