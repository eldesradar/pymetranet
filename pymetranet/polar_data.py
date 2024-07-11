#!/bin/env python

import numpy as np

from pymetranet import PolarSweep, PolarSweepInfo, MomentInfo, MomentUUid

class PolarPpiData:
    _SIZE = 360
    
    def __init__(self, num_gates: int=0):
        self._num_gates = num_gates
        self._mom_id = 0
        self._norm = False
        self._mult = float("nan")
        
        if num_gates == 0:
            self._num_rays = 0
            self._data = None
        else:
            self._num_rays = PolarPpiData.__SIZE
            self._data = np.full((self._SIZE, num_gates), np.nan)
        
    @property
    def num_gates(self) -> int:
        return self._num_gates
        
    @property
    def num_rays(self) -> int:
        return self._num_rays
        
    @property
    def mom_id(self) -> int:
        return self._mom_id
        
    @property
    def norm(self) -> bool:
        return self._norm
        
    @property
    def mult(self) -> float:
        return self._mult
        
    @property
    def data(self):
        return self._data
        
    def get_ray(self, index: int):
        return self._data[index]
        
    def transform(self, sweep: PolarSweep, mom_id: int=None, mom_name: str=None):
        if mom_id is None and mom_name is None:
            raise ValueError("at least one parameter between mom_id or mom_name must not be None")
            
        if mom_id is None:
            #get moment info by name
            mom_info = sweep.get_moment_info_by_name(mom_name)
            if mom_info is None:
                raise ValueError("can't get information of moment '%s'" % mom_name)
            self._mom_id = mom_info.momentid
        else:
            #get moment info by id
            mom_info = sweep.get_moment_info_by_id(mom_id)
            if mom_info is None:
                raise ValueError(f"can't get information of moment id {mom_id}(0x{mom_id:X})")
            self._mom_id = mom_info.momentid
            
        mom = sweep.rays[0].get_moment_by_id(self._mom_id)
        if mom is None:
            raise ValueError(f"can't get reference to moment with id {self._mom_id}(0x{self._mom_id:X})")
            
        self._num_gates = mom.num_gates
        self._num_rays = PolarPpiData._SIZE
        
        #create PolarSweepInfo object to handle moment normalization and multiplier
        sweep_info = PolarSweepInfo(sweep)
        self._norm = self.__detect_norm(sweep_info, mom_info)
        self._mult = self._norm if self.__detect_mult(sweep_info, mom_info) else float("nan")
        
        #initialize internal matrix to all nan
        self._data = np.full((self._SIZE, self._num_gates), np.nan)
        
        #inizialite buff to check for empty slots (used later in this method to prevent holes)
        buff: List[int] = [0] * self._SIZE
        
        #for each ray of sweep
        for i in range(len(sweep.rays)):
            ray = sweep.rays[i]
            mom = ray.get_moment_by_id(self._mom_id)
            if mom is None:
                continue
                
            az_start: int = int(0.5 + ray.get_startaz_deg())
            az_stop: int = int(0.5 + ray.get_endaz_deg())
            if az_stop < az_start:
                if az_stop < (az_start - 10):
                    az_stop += 360
                else:
                    tmp = az_start
                    az_start = az_stop
                    az_stop = tmp
            elif az_start < az_stop:
                if az_stop > 355 and az_start < 5:
                    az_start += 360
                    tmp = az_start
                    az_start = az_stop
                    az_stop = tmp
                    
            for j in range(az_start, az_stop+1):
                az = j
                
                #make some adjustments to 'az'
                if az > 359:
                    az -= 360
                elif az < 0:
                    az += 360
                
                #correction to prevent holes
                if j == az_stop and buff[az] != 0:
                   continue;
                buff[az] += 1
                
                #copy the value in the internal matrix at the index 'az' 'k'
                for k in range(self._num_gates):
                    self._data[az][k] = mom.get_real_value(mom_info, k) * self._mult if self._norm else mom.get_real_value(mom_info, k)
        
    def init_from(self):
        pass
        
    def resize(self):
        pass
        
    def polar2rect(self):
        pass
        
    def __detect_norm(self, sweep_info: PolarSweepInfo, mom_info: MomentInfo) -> bool:
        if mom_info.momentid in [MomentUUid.W, MomentUUid.W_V]:
            return sweep_info.is_width_normalized()
        elif mom_info.momentid in [MomentUUid.V, MomentUUid.V_V,
                MomentUUid.V_PPP, MomentUUid.V_PPP_V]:
            return sweep_info.is_velocity_normalized()
        elif mom_info.momentid in [MomentUUid.PHIDP, MomentUUid.PHIDP_F]:
            return sweep_info.is_phidp_normalized()
        else:
            return False
        
    def __detect_mult(self, sweep_info: PolarSweepInfo, mom_info: MomentInfo) -> float:
        if mom_info.momentid in [MomentUUid.W, MomentUUid.W_V]:
            return sweep_info.get_width_nyquist()
        elif mom_info.momentid in [MomentUUid.V, MomentUUid.V_V,
                MomentUUid.V_PPP, MomentUUid.V_PPP_V]:
            return sweep_info.get_velocity_nyquist()
        elif mom_info.momentid in [MomentUUid.PHIDP, MomentUUid.PHIDP_F]:
            return sweep_info.get_phidp_phase()
        else:
            return 1

