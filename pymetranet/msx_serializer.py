import struct
from abc import ABC, abstractmethod

from .volumesweep import PolarSweep
from .volumesweep import  Ray, Moment, DataMomentHeader
  
class MSxSerializer(ABC):
    def __init__(self):
        self.eof = True
        
    @staticmethod
    def stringify(data):
        return data.decode("utf_8").rstrip('\x00')
    
    def load(self, file_name):
        f = open(file_name, "rb")
        
        ret_sweep = PolarSweep()
        self.eof = False
        
        #read sweep header
        ret_sweep.sweepheader = self.read_sweep_header(f)
        if self.eof:
            return None
            
        #read rays
        while not self.eof:
            ray = Ray()
            
            #read ray header
            ray.rayheader = self.read_ray_header(f)
            if self.eof:
                break
            
            #for each moment
            for i in range(ret_sweep.sweepheader.nummoments):
                moment = Moment()
                mom_info = ret_sweep.sweepheader.momentsinfo[i]
                
                #read moment header and gates
                moment.datamomentheader = self.read_moment_header(f)
                if self.eof:
                    break
                moment.gates = self.read_moment_gates(f, moment.datamomentheader, mom_info.dataformat)
                if self.eof:
                    break
                
                ray.moments.append(moment)
            
            ret_sweep.rays.append(ray)
        
        f.close()
        
        return ret_sweep

    @abstractmethod
    def read_sweep_header(self):
        """
        Subclasses must implement this method
        """
        pass

    @abstractmethod
    def read_ray_header(self):
        """
        Subclasses must implement this method
        """
        pass

    def read_moment_header(self, f):
        ret_data_moment_header = DataMomentHeader()
        
        fmt = "=II"
        struct_len = struct.calcsize(fmt)
        data = f.read(struct_len)
        if not data:
            f.close()
            self.eof = True
            raise Exception("Error reading data moment header")
        s = struct.Struct(fmt)
        unpacked_data = s.unpack(data)
        
        ret_data_moment_header.momentid = unpacked_data[0]
        ret_data_moment_header.datasize = unpacked_data[1]
        
        return ret_data_moment_header
    
    def read_moment_gates(self, f, mom_header, data_format):
        if data_format == 1: #Fixed8Bit
            num_ele = int(mom_header.datasize / 1)
            fmt = "=%dB" % num_ele
        elif data_format == 2: #Float32Bit
            num_ele = int(mom_header.datasize / 4)
            fmt = "=%df" % num_ele
        elif data_format == 3: #Fixed16Bit
            num_ele = int(mom_header.datasize / 2)
            fmt = "=%dH" % num_ele
        else:
            f.close()
            self.eof = True
            raise Exception("Error reading moment gates: unrecognized data format")
        
        struct_len = struct.calcsize(fmt)
        data = f.read(struct_len)
        if not data:
            f.close()
            self.eof = True
            raise Exception("Error reading moment gates")
        s = struct.Struct(fmt)
        unpacked_data = s.unpack(data)
        
        ret_gates = [None] * num_ele
        for i in range(len(unpacked_data)):
            ret_gates[i] = unpacked_data[i]
        
        return ret_gates
        