#!/bin/env python

import math
from enum import IntEnum
from typing import List

from .xml_util import XmlUtil

class DataMomentHeader:
    def __init__(self):
        self.momentid = 0
        self.datasize = 0
        
class MomentUUid(IntEnum):
    #RSP moments
    W       = 0x00000001
    V       = 0x00000002
    UZ      = 0x00000003
    Z       = 0x00000004
    ZDR     = 0x00000005
    RHO     = 0x00000006
    PHIDP   = 0x00000007
    IQ      = 0x00000008
    BURST   = 0x00000009
    SNR     = 0x0000000A
    Z_V     = 0x0000000B
    LDR     = 0x0000000C
    STAT1   = 0x0000000D
    SQI     = 0x0000000E
    SNR_V   = 0x0000000F
    CCR     = 0x00000010
    UW      = 0x00000011
    UV      = 0x00000012
    UUZ     = 0x00000013
    W_V     = 0x00000014
    V_V     = 0x00000015
    UZ_V    = 0x00000016
    CCR_V   = 0x00000017
    STAT2   = 0x00000018
    APH     = 0x00000019
    SQI_V   = 0x0000001A
    WBN     = 0x0000001B
    WBN_V   = 0x0000001C
    V_PPP   = 0x0000001D
    V_PPP_V = 0x0000001E
                    
    #RCP moments
    #...
            
    #RDP moments
    CLUT     = 0x00020001
    Z_CLUT   = 0x00020002
    Z_V_CLUT = 0x00020003
    KDP_RDP  = 0x00020004
    PHIDP_F  = 0x00020005
    Z_C      = 0x00020006
    ZDR_C    = 0x00020007
    
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
    _K_CONV_DEG = 360.0 / 65535.0
    
    def __init__(self):
        self.rayheader = RayHeader()
        self.moments = []
        
    def get_moment_by_id(self, mom_id: int):
        for mom in self.moments:
            if mom.datamomentheader.momentid == mom_id:
                return mom
                
        return None
        
    def get_startaz_deg(self) -> float:
        return Ray.get_az_deg(self.rayheader.startangle)
        
    def get_endaz_deg(self) -> float:
        return Ray.get_az_deg(self.rayheader.endangle)
        
    @staticmethod
    def get_az_deg(value: int) -> float:
        return (value & 0x0000FFFF) * Ray._K_CONV_DEG
        
    def get_startel_deg(self) -> float:
        return Ray.get_el_deg(self.rayheader.startangle)
        
    def get_endel_deg(self) -> float:
        return Ray.get_el_deg(self.rayheader.endangle)
        
    @staticmethod
    def get_el_deg(value: int) -> float:
        return 0 if (value >> 16) == 0xFFFF else (value >> 16) * Ray._K_CONV_DEG

class Moment:
    def __init__(self):
        self.datamomentheader = DataMomentHeader()
        self.gates = []
        
    @property
    def num_gates(self) -> int:
        return len(self.gates)
        
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
    
    @staticmethod
    def get_real_from_dn(mom_info: MomentInfo, dn: int) -> float:
        if mom_info.scaletype == MomentInfo.SCALE_TYPE_LINEAR:
            if mom_info.dataformat in [MomentInfo.DATA_FORMAT_FIXED_8_BIT,
                    MomentInfo.DATA_FORMAT_FIXED_16_BIT]:
                #apply same formula for 8bit or 16bit data
                return (mom_info.factora * dn) + mom_info.factorb
            else:
                #can't do this if format is float
                return float("nan")
        elif mom_info.scaletype == MomentInfo.SCALE_TYPE_LOG:
            if mom_info.dataformat in [MomentInfo.DATA_FORMAT_FIXED_8_BIT,
                    MomentInfo.DATA_FORMAT_FIXED_16_BIT]:
                #apply same formula for 8bit or 16bit data
                return mom_info.factora + mom_info.factorc * \
                    math.pow(10, (1 - dn) / mom_info.factorb)
            else:
                #can't do this if format is float
                return float("nan")
        else:
            return float("nan")
        
class PolarSweep:
    def __init__(self):
        self.sweepheader = SweepHeader()
        self.rays: List[Ray] = []
        
    def get_moment_info_by_name(self, mom_name: str):
        for mom_info in self.sweepheader.momentsinfo:
            if mom_info.name == mom_name:
                return mom_info
                
        return None

    def get_moment_info_by_id(self, mom_id: int) -> MomentInfo:
        for mom_info in self.sweepheader.momentsinfo:
            if mom_info.momentid == mom_id:
                return mom_info
                
        return None
        
class PolMode(IntEnum):
    Undefined = 0
    H = 1
    V = 2
    HV = 3
    HHV = 4
    SIM_HV = 5
    
class PolarSweepInfo:
    def __init__(self, sweep: PolarSweep=None):
        if sweep is None:
            self.__set_fail()
        else:
            self.set(sweep)
        
    def set(self, sweep: PolarSweep):
        if self.__get_fields_for_nyquist(sweep) != 0:
            self.__set_fail()
            return
            
        #here wave length, pol mode, base prf and dprf are already set
        #due to the __get_fields_for_nyquist() call
        
        #get reference to MomentInfo of W, if it's not found we set
        #normalized to false as default
        mom_info = sweep.get_moment_info_by_id(MomentUUid.W)
        if mom_info is None:
            raise ValueError("can't get information of moment W to detect if width is normalized")
        self._is_width_norm = mom_info is None if False else self.__detect_width_normalized(mom_info)
        
        #get reference to MomentInfo of V, if it's not found we set
        #normalized to false as default
        mom_info = sweep.get_moment_info_by_id(MomentUUid.V)
        if mom_info is None:
            raise ValueError("can't get information of moment W to detect if velocity is normalized")
        self._is_vel_norm = mom_info is None if False else self.__detect_velocity_normalized(mom_info)
        
        #get reference to MomentInfo of PHIDP, if it's not found we set
        #normalized to false as default
        mom_info = sweep.get_moment_info_by_id(MomentUUid.PHIDP)
        if mom_info is None:
            raise ValueError("can't get information of moment PHIDP to detect if phase is normalized")
        self._is_phidp_norm = mom_info is None if False else self.__detect_phidp_normalized(mom_info)
        
        self._v_nyquist = self.__calc_velocity_nyquist()
        self._w_nyquist = self.__calc_width_nyquist()
        self._phidp_phase = self.__calc_phidp_phase()
        self._low_prf = self.__calc_low_prf()
        self._is_good = True
        
    def is_width_normalized(self) -> bool:
        return self._is_width_norm
        
    def is_velocity_normalized(self) -> bool:
        return self._is_vel_norm
        
    def is_phidp_normalized(self) -> bool:
        return self._is_phidp_norm
        
    def get_wave_length(self) -> float:
        return self._wave_len
        
    def get_base_prf(self) -> float:
        return self._base_prf
        
    def get_high_prf(self) -> float:
        return self._base_prf
        
    def get_low_prf(self) -> float:
        return self._low_prf
        
    def get_dprf(self) -> int:
        return self._dprf
        
    def get_pol_mode(self) -> PolMode:
        return self._pol_mode
        
    def get_width_nyquist(self) -> float:
        return self._w_nyquist
        
    def get_velocity_nyquist(self) -> float:
        return self._v_nyquist
        
    def get_phidp_phase(self) -> float:
        return self._phidp_phase
        
    def is_good(self) -> bool:
        self._is_good
        
    def __set_fail(self) -> None:
        self._is_good = False
        self._is_width_norm = False
        self._is_vel_norm = False
        self._is_phidp_norm = False
        self._wave_len = float("nan")
        self._base_prf = float("nan")
        self._low_prf = float("nan")
        self._v_nyquist = float("nan")
        self._w_nyquist = float("nan")
        self._dprf = -1
        self._phidp_phase = -1
        self._pol_mode = PolMode.Undefined
        
    def __detect_width_normalized(self, mom_info: MomentInfo) -> bool:
        if mom_info.dataformat == MomentInfo.DATA_FORMAT_FLOAT_32_BIT:
            return False    #can't detect, return false as default

        dn = 0
        if mom_info.dataformat == MomentInfo.DATA_FORMAT_FIXED_8_BIT:
            dn = 0xFF
        elif mom_info.dataformat == MomentInfo.DATA_FORMAT_FIXED_16_BIT:
            dn = 0xFFFF

        #here 'dn' can't be zero, it's an impossible scenario, anyway
        #for safety we do an extra check to be sure dn is properly set,
        #otherwise return false as default
        if dn == 0:
            return False

        max_real_value = Moment.get_real_from_dn(mom_info, dn)
        if math.isnan(max_real_value):
            return False

        diff = abs(max_real_value - 1)
        if diff < 1:
            return True #normalized
        else:
            return False #NOT normalized
        
    def __detect_velocity_normalized(self, mom_info: MomentInfo) -> bool:
        #same logic of width
        return self.__detect_width_normalized(mom_info)
        
    def __detect_phidp_normalized(self, mom_info: MomentInfo) -> bool:
        #same logic of width
        return self.__detect_width_normalized(mom_info)
        
    def __calc_width_nyquist(self) -> float:
        nyquist_w = float("nan")
        ny_factor = 0.0025
        
        if self._pol_mode == PolMode.HV:
            ny_factor = 0.00125
        
        nyquist_w = self._wave_len * self._base_prf * ny_factor
        
        return nyquist_w
        
    def __calc_velocity_nyquist(self) -> float:
        nyquist_v = float("nan")
        ny_factor = 0.0025
        
        if self._pol_mode == PolMode.HV:
            ny_factor = 0.00125
        
        if self._dprf > 1:
            nyquist_v = self._wave_len * self._base_prf  * self._dprf * ny_factor
        else:
            nyquist_v = self._wave_len * self._base_prf  * ny_factor
        
        return nyquist_v
        
    def __calc_phidp_phase(self) -> int:
        if self._pol_mode in [PolMode.HV, PolMode.HHV]:
            return 90
        else:
            return 180
        
    def __calc_low_prf(self) -> float:
        if self._dprf == 2:
            return self._base_prf * 2.0 / 3.0
        elif self._dprf == 3:
                return self._base_prf * 3.0 / 4.0
        elif self._dprf == 4:
            return self._base_prf * 4.0 / 5.0
        else:
            return self._base_prf
        
    def __get_fields_for_nyquist(self, sweep: PolarSweep) -> int:
        if len(sweep.rays) == 0:
            return -1  # error

        self._wave_len = sweep.sweepheader.wavelength
        self._pol_mode = PolMode.Undefined

        ray_header_prf = sweep.rays[0].rayheader.prf
        ray_header_dprf = sweep.rays[0].rayheader.dataflags & 0x0000000F

        if math.isnan(ray_header_prf):
            return -1  # error

        #check metadata
        meta_data = sweep.sweepheader.metadata
        if not meta_data:
            #in this case metadata is not present, we assume the prf is 'base prf'
            #as the standard says. It is assumed that this MSx file
            #contains 'standard' values regarding the prf
            self._base_prf = ray_header_prf
            self._dprf = ray_header_dprf
            return 0  #all ok

        #parse metadata and try to read prf and dprf
        sweep_data = XmlUtil.parse_sweep_data(meta_data)
        meta_data_prf = float(sweep_data.rsp_cmd.prf)
        meta_data_dprf = int(sweep_data.rsp_cmd.dprf)
        if meta_data_prf == 0.0 or meta_data_dprf == 0:
            #can't parse prf or dprf in the metada section, we assume the
            #prf is 'base prf' as the standard says. It is assumed that this
            #MSx file contains 'standard' values regarding the prf
            self._base_prf = ray_header_prf
            self._dprf = ray_header_dprf
        else:
            #prf and dprf parsed correctly from the metadata
            self._base_prf = meta_data_prf
            self._dprf = meta_data_dprf

        #try to parse polarization mode from the metadata
        if sweep_data.rsp_cmd.pol == "4 1":
            self._pol_mode = PolMode.H
        elif sweep_data.rsp_cmd.pol == "4 2":
            self._pol_mode = PolMode.V
        elif sweep_data.rsp_cmd.pol == "4 3":
            self._pol_mode = PolMode.HV
        elif sweep_data.rsp_cmd.pol == "4 4":
            self._pol_mode = PolMode.HHV
        elif sweep_data.rsp_cmd.pol == "2 3":
            self._pol_mode = PolMode.SIM_HV

        #return ok
        return 0

