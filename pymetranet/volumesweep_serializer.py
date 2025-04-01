#!/bin/env python3

import ctypes

from .msx_serializer_v1 import MSxV1Serializer
from .msx_serializer_v2 import MSxV2Serializer

class SweepHeaderRawCommon(ctypes.LittleEndianStructure):
    """
    Represents the common header structure for sweep files in little-endian format.

    Attributes:
        fileid (bytes): File identifier (4 bytes).
        version (int): File version (1 byte).
        spare1 (list[int]): Reserved bytes (3 bytes).
        length (int): Total length of the header (4 bytes).
    """
    _fields_ = [
        ("fileid", ctypes.c_char * 4),  #4:4
        ("version", ctypes.c_uint8),    #1:5
        ("spare1", ctypes.c_uint8 * 3), #3:8
        ("length", ctypes.c_uint32),    #4:12
    ]

class PolarSweepSerializer:
    """
    Serializer for polar sweep files. Determines the file version based on the header
    and delegates loading to the appropriate concrete serializer (MSxV1Serializer or MSxV2Serializer).
    """

    @staticmethod
    def test_load(file_name) -> int:
        """
        Tests the specified file to check if it is a valid sweep file and determines its version.

        This method reads the header from the file, verifies that the 'fileid' field matches "EDPF",
        and returns the version (1 or 2) if recognized. If the file cannot be read or is not valid,
        it returns None.

        Args:
            file_name (str): The path to the file to test.

        Returns:
            int: The version of the file (1 or 2) if recognized; None otherwise.
        """
        f = open(file_name, "rb")
        rec = SweepHeaderRawCommon()
        read = f.readinto(rec)
        if not read:
            f.close()
            return None
        f.close()
        
        #check if FileId is 'EDPF'
        if rec.fileid != b"EDPF":
            return None

        #determine version of the file and use appropriate
        #concrete serializer
        if rec.version == 1:
            return 1
        elif rec.version == 2:
            return 2
        else:
            return None
            
        return None
    
    @staticmethod
    def load(file_name):
        """
        Loads and deserializes a polar sweep file.

        This method reads the file header, verifies that the 'fileid' field is "EDPF", and determines
        the file version. It then uses the appropriate concrete serializer (MSxV1Serializer or MSxV2Serializer)
        to load the file.

        Args:
            file_name (str): The path to the file to load.

        Returns:
            Any: The result of the concrete serializer's load() method.

        Raises:
            Exception: If the header cannot be read, if the fileid is invalid, or if the file version is unrecognized.
        """
        f = open(file_name, "rb")
        rec = SweepHeaderRawCommon()
        read = f.readinto(rec)
        if not read:
            f.close()
            raise Exception("Can't read sweep header")
        f.close()
        
        #check if FileId is 'EDPF'
        if rec.fileid != b"EDPF":
            raise Exception("Bad file id") 

        #determine version of the file and use appropriate
        #concrete serializer
        if rec.version == 1:
            serializer = MSxV1Serializer()
            return serializer.load(file_name)
        elif rec.version == 2:
            serializer = MSxV2Serializer()
            return serializer.load(file_name)
        else:
            raise Exception("Unrecognized MSx file version")
            
        return None
