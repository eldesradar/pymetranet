#!/bin/env python

import ctypes

from .msx_serializer_v1 import MSxV1Serializer
from .msx_serializer_v2 import MSxV2Serializer

class SweepHeaderRawCommon(ctypes.LittleEndianStructure):
    _fields_ = [
        ("fileid", ctypes.c_char * 4),  #4:4
        ("version", ctypes.c_uint8),    #1:5
        ("spare1", ctypes.c_uint8 * 3), #3:8
        ("length", ctypes.c_uint32),    #4:12
    ]

class PolarSweepSerializer:
    @staticmethod
    def load(file_name):
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
