#!/bin/env python3

import struct
from .volumesweep import SweepHeader, MomentInfo
from .volumesweep import  RayHeader
from .volumesweep import BatchInfo
from .msx_serializer import MSxSerializer
        
class MSxV2Serializer(MSxSerializer):
    def __init__(self):
        super().__init__()
        
    def read_sweep_header(self, f):
        ret_sweepheader = SweepHeader()
        
        fmt = "=4sB3BI16s16sfffBBBBBB2BHHffffI"
        struct_len = struct.calcsize(fmt)
        data = f.read(struct_len)
        if not data:
            f.close()
            self.eof = True
            raise Exception("Error reading sweep header")
        s = struct.Struct(fmt)
        unpacked_data = s.unpack(data)
        
        ret_sweepheader.fileid = unpacked_data[0]
        ret_sweepheader.version = unpacked_data[1]
        #unpacked_data[2], 3 and 4 are spare
        ret_sweepheader.length = unpacked_data[5]
        ret_sweepheader.radarname = MSxSerializer.stringify(unpacked_data[6])
        ret_sweepheader.scanname = MSxSerializer.stringify(unpacked_data[7])
        ret_sweepheader.radarlat = unpacked_data[8]
        ret_sweepheader.radarlon = unpacked_data[9]
        ret_sweepheader.radarheight = unpacked_data[10]
        ret_sweepheader.sequencesweep = unpacked_data[11]
        ret_sweepheader.currentsweep = unpacked_data[12]
        ret_sweepheader.totalsweep = unpacked_data[13]
        ret_sweepheader.antmode = unpacked_data[14]
        ret_sweepheader.priority = unpacked_data[15]
        ret_sweepheader.quality = unpacked_data[16]
        #unpacked_data[17] and 18 are spare
        ret_sweepheader.repeattime = unpacked_data[19]
        ret_sweepheader.nummoments = unpacked_data[20]
        ret_sweepheader.gatewidth = unpacked_data[21]
        ret_sweepheader.wavelength = unpacked_data[22]
        ret_sweepheader.pulsewidth = unpacked_data[23]
        ret_sweepheader.startrange = unpacked_data[24]
        ret_sweepheader.metadatasize = unpacked_data[25]
        
        #read moments information
        fmt = "=IBBBB12s12sfffB3B"
        struct_len = struct.calcsize(fmt)
        s = struct.Struct(fmt)
        for i in range(ret_sweepheader.nummoments):
            data = f.read(struct_len)
            if not data:
                f.close()
                self.eof = True
                raise Exception("Error reading moment info structure")
            unpacked_data = s.unpack(data)
            
            mom_info = MomentInfo()
            mom_info.momentid = unpacked_data[0]
            mom_info.dataformat = unpacked_data[1]
            mom_info.numbytes = unpacked_data[2]
            mom_info.normalized = (unpacked_data[3] & 0x01) == 1
            #unpacked_data[4] is spare
            mom_info.name = MSxSerializer.stringify(unpacked_data[5])
            mom_info.unit = MSxSerializer.stringify(unpacked_data[6])
            mom_info.factora = unpacked_data[7]
            mom_info.factorb = unpacked_data[8]
            mom_info.factorc = unpacked_data[9]
            mom_info.scaletype = unpacked_data[10]
            #unpacked_data[11], 12 and 13 are spare
            
            ret_sweepheader.momentsinfo.append(mom_info)
        
        #read sweep metadata
        if ret_sweepheader.metadatasize > 0:
            fmt = "=%ds" % ret_sweepheader.metadatasize
            struct_len = struct.calcsize(fmt)
            s = struct.Struct(fmt)
            data = f.read(struct_len)
            if not data:
                f.close()
                self.eof = True
                raise Exception("Error reading sweep header metadata")
            unpacked_data = s.unpack(data)
            
            ret_sweepheader.metadata = MSxSerializer.stringify(unpacked_data[0])
            
        return ret_sweepheader
        
    def read_ray_header(self, f):
        ret_rayheader = RayHeader()
        
        fmt = "=IIIHHIfQIIH6B"
        struct_len = struct.calcsize(fmt)
        data = f.read(struct_len)
        if not data:
            self.eof = True
            return None
        s = struct.Struct(fmt)
        unpacked_data = s.unpack(data)
        
        ret_rayheader.length = unpacked_data[0]
        ret_rayheader.startangle = unpacked_data[1]
        ret_rayheader.endangle = unpacked_data[2]
        ret_rayheader.sequence = unpacked_data[3]
        ret_rayheader.numpulses = unpacked_data[4]
        ret_rayheader.databytes = unpacked_data[5]
        ret_rayheader.prf = unpacked_data[6]
        ret_rayheader.datetime = unpacked_data[7]
        ret_rayheader.dataflags = unpacked_data[8]
        ret_rayheader.metadatasize = unpacked_data[9]
        ret_rayheader.numbatches = unpacked_data[10]
        #unpacked_data[11], 12, 13, 14, 15 and 16 are spare
        
        #read batches information
        fmt = "=IffHHf"
        struct_len = struct.calcsize(fmt)
        s = struct.Struct(fmt)
        for i in range(ret_rayheader.numbatches):
            data = f.read(struct_len)
            if not data:
                f.close()
                self.eof = True
                raise Exception("Error reading batch info structure")
            unpacked_data = s.unpack(data)
            
            batch_info = BatchInfo()
            batch_info.length = unpacked_data[0]
            batch_info.startrange = unpacked_data[1]
            batch_info.prf = unpacked_data[2]
            batch_info.numpulses = unpacked_data[3]
            batch_info.dprf = unpacked_data[4]
            batch_info.angperc = unpacked_data[5]
            
            ret_rayheader.batchesinfo.append(batch_info)
        
        #read ray metadata
        if ret_rayheader.metadatasize > 0:
            fmt = "=%ds" % ret_rayheader.metadatasize
            struct_len = struct.calcsize(fmt)
            s = struct.Struct(fmt)
            data = f.read(struct_len)
            if not data:
                f.close()
                self.eof = True
                raise Exception("Error reading ray header metadata")
            unpacked_data = s.unpack(data)
            
            ret_rayheader.metadata = MSxSerializer.stringify(unpacked_data[0])
        
        return ret_rayheader
