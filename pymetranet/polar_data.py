#!/bin/env python3

from typing import List
import math
import numpy as np

from .volumesweep import PolarSweep, PolarSweepInfo, MomentInfo, MomentUUid, Moment
from .cmd_line_params import MapSizeRect

class PolarPpiData:
    """
    Represents PPI (Plan Position Indicator) data derived from polar sweep data.

    The class stores the number of gates and rays, along with the moment data for each ray.
    It also supports transforming the data using sweep and moment information, and converting
    polar data to rectangular (Cartesian) data.

    Attributes:
        _SIZE (int): Constant size for the number of rays (360).
        _num_gates (int): Number of gates.
        _num_rays (int): Number of rays; defaults to _SIZE.
        _mom_id (int): Moment ID used for transformation.
        _norm (bool): Flag indicating if the moment data is normalized.
        _mult (float): Multiplication factor to apply when data is normalized.
        _data (np.ndarray): 2D array holding the PPI data.
    """
    _SIZE = 360
    
    def __init__(self, num_gates: int=0, data: np.ndarray=None):
        """
        Initializes a new PolarPpiData object.

        If num_gates is 0, no data matrix is created. Otherwise, a matrix of size (_SIZE x num_gates)
        is initialized (filled with NaNs) unless provided via the 'data' parameter.

        Args:
            num_gates (int, optional): Number of gates. Defaults to 0.
            data (np.ndarray, optional): Pre-existing data array. Defaults to None.
        """
        self._num_gates = num_gates
        self._mom_id = 0
        self._norm = False
        self._mult = float("nan")
        
        if num_gates == 0:
            self._num_rays = 0
            self._data = None
        else:
            self._num_rays = PolarPpiData._SIZE
            self._data = data if data is not None else np.full((self._SIZE, num_gates), np.nan)
        
    @property
    def num_gates(self) -> int:
        """
        Gets the number of gates.

        Returns:
            int: The number of gates.
        """
        return self._num_gates
        
    @property
    def num_rays(self) -> int:
        """
        Gets the number of rays.

        Returns:
            int: The number of rays.
        """
        return self._num_rays
        
    @property
    def mom_id(self) -> int:
        """
        Gets the moment ID used for transformation.

        Returns:
            int: The moment ID.
        """
        return self._mom_id
        
    @property
    def norm(self) -> bool:
        """
        Indicates whether the moment data is normalized.

        Returns:
            bool: True if normalized, False otherwise.
        """
        return self._norm
        
    @property
    def mult(self) -> float:
        """
        Gets the multiplication factor applied when data is normalized.

        Returns:
            float: The multiplication factor.
        """
        return self._mult
        
    @property
    def data(self) -> np.ndarray:
        """
        Gets the internal 2D data array.

        Returns:
            np.ndarray: The PPI data array.
        """
        return self._data
    
    @data.setter
    def data(self, value: np.ndarray) -> None:
        """
        Sets the internal 2D data array.

        Verifies that the array has two dimensions with the first dimension equal to _SIZE.
        Updates internal properties accordingly.

        Args:
            value (np.ndarray): The new data array.
        """
        #verify shape
        assert len(value.shape) == 2
        assert value.shape[0] == self._SIZE
        assert value.shape[1] > 0

        #set internal members
        self._num_gates = value.shape[1]
        self._mom_id = 0
        self._norm = False
        self._mult = float("nan")
        self._num_rays = PolarPpiData._SIZE
        self._data = value
        
    def get_ray(self, index: int) -> np.ndarray:
        """
        Retrieves the data for a specific ray by index.

        Args:
            index (int): The index of the ray.

        Returns:
            np.ndarray: The data array corresponding to the ray.
        """
        return self._data[index]
        
    def transform(self, sweep: PolarSweep, mom_id: int=None, mom_name: str=None):
        """
        Transforms the PPI data based on a given polar sweep and moment information.

        This method selects the appropriate moment data from the sweep (using either a moment ID
        or moment name), updates internal parameters, and fills the internal data array with
        transformed values. It applies normalization and multiplication factors if applicable.

        Args:
            sweep (PolarSweep): The polar sweep containing the moment data.
            mom_id (int, optional): The moment ID. Defaults to None.
            mom_name (str, optional): The moment name. Defaults to None.

        Raises:
            ValueError: If neither mom_id nor mom_name is provided or if moment information cannot be retrieved.
        """
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
        self._mult = self.__detect_mult(sweep_info, mom_info) if self._norm else float("nan")
        
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
        
    @staticmethod
    def build_az_range_matrix(sweep: PolarSweep, mom_id: int=None, mom_name: str=None) -> np.ndarray:
        """
        Builds and returns an azimuth range matrix from a polar sweep.

        The matrix is constructed from moment data across all rays.
        Normalization and multiplication are applied if applicable.

        Args:
            sweep (PolarSweep): The polar sweep containing the moment data.
            mom_id (int, optional): The moment ID to use. Defaults to None.
            mom_name (str, optional): The moment name to use. Defaults to None.

        Returns:
            np.ndarray: A 2D array representing the azimuth range matrix.

        Raises:
            ValueError: If neither mom_id nor mom_name is provided, or if moment information cannot be retrieved.
        """
        if mom_id is None and mom_name is None:
            raise ValueError("at least one parameter between mom_id or mom_name must not be None")
            
        if mom_id is None:
            #get moment info by name
            mom_info = sweep.get_moment_info_by_name(mom_name)
            if mom_info is None:
                raise ValueError("can't get information of moment '%s'" % mom_name)
            mom_id = mom_info.momentid
        else:
            #get moment info by id
            mom_info = sweep.get_moment_info_by_id(mom_id)
            if mom_info is None:
                raise ValueError(f"can't get information of moment id {mom_id}(0x{mom_id:X})")
            mom_id = mom_info.momentid
            
        mom: Moment = sweep.rays[0].get_moment_by_id(mom_id)
        if mom is None:
            raise ValueError(f"can't get reference to moment with id {self._mom_id}(0x{mom_id:X})")
            
        num_rays = len(sweep.rays)
        num_gates = mom.num_gates
        
        #create PolarSweepInfo object to handle moment normalization and multiplier
        sweep_info = PolarSweepInfo(sweep)
        norm = PolarPpiData.__detect_norm(sweep_info, mom_info)
        mult = PolarPpiData.__detect_mult(sweep_info, mom_info) if norm else float("nan")
        
        #initialize output matrix to all nan
        data = np.full((num_rays, num_gates), np.nan)
        
        #for each ray of sweep
        for i in range(len(sweep.rays)):
            ray = sweep.rays[i]
            mom: Moment = ray.get_moment_by_id(mom_id)
            if mom is None:
                raise ValueError("can't get reference to gates of moment id '%d'" % mom_id)
                
            #copy the value in the output matrix at the index 'i' 'j'
            for j in range(num_gates):
                data[i][j] = mom.get_real_value(mom_info, j) * mult if norm else mom.get_real_value(mom_info, j)

        return data
    
    def init_from(self):
        """
        Initializes the PolarPpiData object from another source.

        (This method is currently a placeholder.)
        """
        pass
        
    def resize(self):
        """
        Resizes the internal data matrix.

        (This method is currently a placeholder.)
        """
        pass

    #if size is not specified or is None polar2rect auto determines
    #the size of the rect considering to generate a square rect
    #with a size of num_gates*2 x num_gates*2 as pixel resolution
    #and an x_res and y_res both equal to the gate_width
    def polar2rect(self, gate_width: float, size: MapSizeRect=None, vectorized: bool=True) -> np.ndarray:
        """
        Converts the polar PPI data to rectangular (Cartesian) coordinates.

        If 'size' is not specified, a square rectangle is automatically determined,
        with dimensions (num_gates*2 x num_gates*2) and x/y resolution equal to gate_width.

        Args:
            gate_width (float): The width of a gate.
            size (MapSizeRect, optional): The target rectangular map size and resolution.
            vectorized (bool, optional): If True, uses the vectorized implementation.
                                         If False, uses a loop-based implementation.
                                         Defaults to True.

        Returns:
            np.ndarray: The resulting rectangular data matrix.
        """
        if vectorized:
            return self.__polar2rect_vectorized(gate_width, size)
        else:
            return self.__polar2rect(gate_width, size)

    #if size is not specified or is None polar2rect auto determines
    #the size of the rect considering to generate a square rect
    #with a size of num_gates*2 x num_gates*2 as pixel resolution
    #and an x_res and y_res both equal to the gate_width
    def __polar2rect(self, gate_width: float, size: MapSizeRect=None) -> np.ndarray:
        """
        Converts polar data to rectangular coordinates using a loop-based approach.

        Args:
            gate_width (float): The width of a gate.
            size (MapSizeRect, optional): The rectangular map size and resolution.
                                          If None, a default square size is used.

        Returns:
            np.ndarray: The rectangular data matrix.
        """
        if size is None:
            x_y_size: int = self.num_gates * 2
            size = MapSizeRect(x_y_size, x_y_size, gate_width, gate_width)

        x_res: float = size.x_res * size.x_res
        y_res: float = size.y_res * size.y_res
        
        radar_x0: float = (size.x_size - 1) * 0.5
        radar_y0: float = (size.y_size - 1) * 0.5

        num_gates: int = self.num_gates
        
        output = np.full((size.y_size, size.x_size), np.nan)
        
        for j in range(size.y_size):
            y = j -radar_y0
            for i in range(size.x_size):
                x = i - radar_x0
                r = math.sqrt(x * x * x_res + y * y * y_res) #in km
                irng = int(r / gate_width + 0.5)
                if irng < num_gates:
                    azimuth = 57.2957795 * math.atan2(x, y)
                    iaz = 180 - int(azimuth)
                    output[j][i] = self._data[iaz][irng]
        
        return output
        
    def __polar2rect_vectorized(self, gate_width: float, size: MapSizeRect=None) -> np.ndarray:
        """
        Converts polar data to rectangular coordinates using a vectorized approach.

        Args:
            gate_width (float): The width of a gate.
            size (MapSizeRect, optional): The rectangular map size and resolution.
                                          If None, a default square size is used.

        Returns:
            np.ndarray: The rectangular data matrix.
        """
        if size is None:
            x_y_size: int = self.num_gates * 2
            size = MapSizeRect(x_y_size, x_y_size, gate_width, gate_width)

        x_res: float = size.x_res
        y_res: float = size.y_res

        radar_x0: float = (size.x_size - 1) * 0.5
        radar_y0: float = (size.y_size - 1) * 0.5

        num_gates: int = self.num_gates

        output = np.full((size.y_size, size.x_size), np.nan)

        # Create meshgrid for x and y coordinates
        y_indices, x_indices = np.meshgrid(np.arange(size.y_size), np.arange(size.x_size), indexing='ij')
        x = (x_indices - radar_x0) * x_res
        y = (y_indices - radar_y0) * y_res

        # Calculate r and azimuth in vectorized form
        r = np.sqrt(x * x + y * y)  # in km
        irng = (r / gate_width + 0.5).astype(int)

        # Calculate azimuth and convert to array index
        azimuth = np.degrees(np.arctan2(x, y))
        iaz = 180 - azimuth.astype(int)

        # Create mask for valid indices
        valid_mask = (irng < num_gates) & (iaz >= 0) & (iaz < 360)

        # Populate the output array
        output[valid_mask] = self._data[iaz[valid_mask], irng[valid_mask]]

        return output
    
    @staticmethod
    def __detect_norm(sweep_info: PolarSweepInfo, mom_info: MomentInfo) -> bool:
        """
        Detects whether the moment data is normalized based on the moment ID.

        For specific moment IDs, it returns the appropriate normalization flag from sweep_info.

        Args:
            sweep_info (PolarSweepInfo): The polar sweep information.
            mom_info (MomentInfo): The moment information.

        Returns:
            bool: True if normalized, False otherwise.
        """
        if mom_info.momentid in [MomentUUid.W, MomentUUid.W_V]:
            return sweep_info.is_width_normalized()
        elif mom_info.momentid in [MomentUUid.V, MomentUUid.V_V,
                MomentUUid.V_PPP, MomentUUid.V_PPP_V]:
            return sweep_info.is_velocity_normalized()
        elif mom_info.momentid in [MomentUUid.PHIDP, MomentUUid.PHIDP_F]:
            return sweep_info.is_phidp_normalized()
        else:
            return False
        
    @staticmethod
    def __detect_mult(sweep_info: PolarSweepInfo, mom_info: MomentInfo) -> float:
        """
        Determines the multiplication factor to apply to the moment data based on normalization.

        Args:
            sweep_info (PolarSweepInfo): The polar sweep information.
            mom_info (MomentInfo): The moment information.

        Returns:
            float: The multiplier value.
        """
        if mom_info.momentid in [MomentUUid.W, MomentUUid.W_V]:
            return sweep_info.get_width_nyquist()
        elif mom_info.momentid in [MomentUUid.V, MomentUUid.V_V,
                MomentUUid.V_PPP, MomentUUid.V_PPP_V]:
            return sweep_info.get_velocity_nyquist()
        elif mom_info.momentid in [MomentUUid.PHIDP, MomentUUid.PHIDP_F]:
            return sweep_info.get_phidp_phase()
        else:
            return 1

