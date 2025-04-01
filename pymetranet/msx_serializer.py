#!/bin/env python3

import struct
from abc import ABC, abstractmethod

from .volumesweep import PolarSweep
from .volumesweep import  Ray, Moment, DataMomentHeader
  
class MSxSerializer(ABC):
    """
    Abstract base class for serializing MSx files.

    This class defines methods for loading a polar sweep from an MSx file.
    It provides common functionality such as reading headers, moments, and gates.
    Subclasses must implement the methods to read the sweep and ray headers.
    
    Attributes:
        eof (bool): Flag indicating if the end-of-file has been reached.
    """
    def __init__(self):
        """
        Initializes an MSxSerializer instance and sets eof to True.
        """
        self.eof = True
        
    @staticmethod
    def stringify(data):
        """
        Converts a bytes object to a UTF-8 string and strips null characters.
        
        Args:
            data (bytes): The bytes object to convert.
            
        Returns:
            str: The decoded and stripped string.
        """
        return data.decode("utf_8").rstrip('\x00')
    
    def load(self, file_name):
        """
        Loads and deserializes an MSx file into a PolarSweep object.

        This method opens the specified file, reads the sweep header,
        iterates over the rays and moments, and populates the PolarSweep object.
        It stops reading if the end-of-file is reached.

        Args:
            file_name (str): The path to the file to load.

        Returns:
            PolarSweep: The deserialized sweep data.
            
        Raises:
            Exception: If an error occurs while reading headers or moment data.
        """
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
        Reads and returns the sweep header from the file.

        Must be implemented by subclasses.

        Args:
            f (file object): The open file object from which to read the sweep header.

        Returns:
            The sweep header object.
        """
        pass

    @abstractmethod
    def read_ray_header(self):
        """
        Reads and returns the ray header from the file.

        Must be implemented by subclasses.

        Args:
            f (file object): The open file object from which to read the ray header.

        Returns:
            The ray header object.
        """
        pass

    def read_moment_header(self, f):
        """
        Reads the moment header from the file.

        Reads a fixed-size binary block from the file, unpacks it, and assigns the values
        to a DataMomentHeader object.

        Args:
            f (file object): The open file object.

        Returns:
            DataMomentHeader: The populated moment header object.
            
        Raises:
            Exception: If the moment header cannot be read.
        """
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
        """
        Reads the moment gates from the file based on the specified data format.

        Args:
            f (file object): The open file object.
            mom_header (DataMomentHeader): The header for the moment, containing datasize.
            data_format (int): The format of the data:
                1 - Fixed 8-bit,
                2 - Float 32-bit,
                3 - Fixed 16-bit.

        Returns:
            list: A list of gate values.

        Raises:
            Exception: If an unrecognized data format is encountered or if gate data cannot be read.
        """
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
        