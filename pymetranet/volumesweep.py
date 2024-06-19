#!/bin/env python

class SweepHeader:
    def __init__(self):
        self.fileid = ""
        self.version = 0
        self.length = 0
        self.radarname = ""
        self.scanname = ""
        self.radarlat = float("nan")
        self.radarlon = float("nan")
        self.radarheight = float("nan")
        self.sequencesweep = -1
        self.currentsweep = -1
        self.totalsweep = -1
        self.antmode = -1
        self.priority = -1
        self.quality = -1
        self.repeattime = -1
        self.nummoments = -1
        self.gatewidth = float("nan")
        self.wavelength = float("nan")
        self.pulsewidth = float("nan")
        self.startrange = float("nan")
        self.metadatasize = 0
        self.momentsinfo = []
        self.metadata = ""

class MomentInfo:
    #types of generators of gates values
    DATA_FORMAT_FIXED_8_BIT = 1
    DATA_FORMAT_FLOAT_32_BIT = 2
    DATA_FORMAT_FIXED_16_BIT = 3
    
    SCALE_TYPE_LINEAR = 1
    SCALE_TYPE_LOG = 2
    
    def __init__(self):
        self.momentid = 0
        self.dataformat = 0
        self.numbytes = 0
        self.normalized = False
        self.name = ""
        self.unit = ""
        self.factora = float("nan")
        self.factorb = float("nan")
        self.factorc = float("nan")
        self.scaletype = 0
        
class RayHeader:
    def __init__(self):
        self.length = 0
        self.startangle = 0
        self.endangle = 0
        self.sequence = 0
        self.numpulses = 0
        self.databytes = 0
        self.prf = float("nan")
        self.datetime = 0
        self.dataflags = 0
        self.metadatasize = 0
        self.numbatches = 0
        self.batchesinfo = []
        self.metadata = ""

class BatchInfo:
    def __init__(self):
        self.length = 0
        self.startrange = float("nan")
        self.prf = float("nan")
        self.numpulses = 0
        self.dprf = 0
        self.angperc = float("nan")
    
class Ray:
    def __init__(self):
        self.rayheader = RayHeader()
        self.moments = []

class Moment:
    def __init__(self):
        self.datamomentheader = DataMomentHeader()
        self.gates = []
        
    def get_real_value(self, mom_info, index):
        if mom_info.scaletype == MomentInfo.SCALE_TYPE_LINEAR:
            if mom_info.dataformat == MomentInfo.DATA_FORMAT_FLOAT_32_BIT:
                return self.gates[index]

            if self.gates[index] == 0:
                return float("nan")

            return (mom_info.factora * self.gates[index]) + mom_info.factorb
        elif mom_info.scaletype == MomentInfo.SCALE_TYPE_LOG:
            if mom_info.dataformat == MomentInfo.DATA_FORMAT_FLOAT_32_BIT:
                return self.gates[index]

            if self.gates[index] == 0:
                return float("nan")

            exp =  (1 - self.gates[index]) / mom_info.factorb
            return mom_info.factora + mom_info.factorc * pow(10, exp)

        return float("nan")

class DataMomentHeader:
    def __init__(self):
        self.momentid = 0
        self.datasize = 0
    
class PolarSweep:
    def __init__(self):
        self.sweepheader = SweepHeader()
        self.rays = []
