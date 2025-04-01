#!/bin/env python3

from bisect import bisect_left
from typing import List, Tuple
import math
import numpy as np

class GeoRefGate:
    """
    Represents a single gate with geographical reference information.

    Attributes:
        _gate_index (int): The index of the gate.
        _gate_mid_height (float): The mid height of the gate.
        _horizon_distance (float): The horizon distance for the gate.
    """
    def __init__(self, gate_index: int=-1, gate_mid_height: float=float("nan"), horizon_distance: float=float("nan")):
        """
        Initializes a GeoRefGate instance.

        Args:
            gate_index (int, optional): The index of the gate. Defaults to -1.
            gate_mid_height (float, optional): The mid height of the gate. Defaults to NaN.
            horizon_distance (float, optional): The horizon distance for the gate. Defaults to NaN.
        """
        self._gate_index = gate_index
        self._gate_mid_height = gate_mid_height
        self._horizon_distance = horizon_distance

    @property
    def gate_index(self) -> int:
        """
        Gets the gate index.

        Returns:
            int: The gate index.
        """
        return self._gate_index
    
    @gate_index.setter
    def gate_index(self, value: int) -> None:
        """
        Sets the gate index.

        Args:
            value (int): The new gate index.
        """
        self._gate_index = value

    @property
    def gate_mid_height(self) -> float:
        """
        Gets the gate's mid height.

        Returns:
            float: The gate mid height.
        """
        return self._gate_mid_height
    
    @gate_mid_height.setter
    def gate_mid_height(self, value: float) -> None:
        """
        Sets the gate's mid height.

        Args:
            value (float): The new mid height value.
        """
        self._gate_mid_height = value

    @property
    def horizon_distance(self) -> float:
        """
        Gets the gate's horizon distance.

        Returns:
            float: The horizon distance.
        """
        return self._horizon_distance
    
    @horizon_distance.setter
    def horizon_distance(self, value: float) -> None:
        """
        Sets the gate's horizon distance.

        Args:
            value (float): The new horizon distance.
        """
        self._horizon_distance = value

class GeoReference:
    """
    Performs geographical reference calculations for radar data.

    This class calculates the mid-height and horizon distance for each gate of a radar sweep,
    based on the radar's elevation, gate width, and height.

    Attributes:
        _data (List[GeoRefGate]): List of GeoRefGate objects.
        _elevation (float): The elevation angle (in degrees).
        _gate_width (float): The width of each gate.
    """
    _ERADIUS = 6371000.0 * 4.0 / 3.0
    _EARTH_RADIUS = _ERADIUS * 0.001
    _EARTH_RADIUS2 = _EARTH_RADIUS * _EARTH_RADIUS

    def __init__(self):
        """
        Initializes a new GeoReference instance.
        """
        self._data: List[GeoRefGate] = []
        self._elevation: float = float("nan")
        self._gate_width: float = float("nan")
    
    @property
    def elevation(self) -> float:
        """
        Gets the elevation angle.

        Returns:
            float: The elevation angle (in degrees).
        """
        return self._elevation
    
    @property
    def gate_width(self) -> float:
        """
        Gets the gate width.

        Returns:
            float: The width of each gate.
        """
        return self._gate_width
    
    @property
    def data(self) -> List[GeoRefGate]:
        """
        Gets the list of GeoRefGate objects.

        Returns:
            List[GeoRefGate]: The list of gate reference data.
        """
        return self._data

    def build(self, src_ray: np.ndarray, elevation: float, gate_width: float, radar_height: float) -> None:
        """
        Calculates and builds the geographical reference data for each gate.

        For each gate in the source ray, this method computes the gate's mid height and
        horizon distance using the provided radar elevation, gate width, and radar height.
        The results are stored internally as a list of GeoRefGate objects.

        Args:
            src_ray (np.ndarray): The source ray data (1D array length determines number of gates).
            elevation (float): The radar elevation angle in degrees.
            gate_width (float): The width of each gate.
            radar_height (float): The height of the radar.

        Returns:
            None
        """
        #clear data
        self._data.clear()
        
        #resize data with size of source
        self._data = [GeoRefGate() for _ in range(len(src_ray))]
        
        self._elevation = elevation
        self._gate_width = gate_width
        
        #for each gate of source ray, calculate gate height
        #and horizon distance and populate internal data ray
        num_gates: int = len(src_ray)
        elev_rad: float = math.radians(elevation)
        sin_elev: float = math.sin(elev_rad)
        cos_elev: float = math.cos(elev_rad)
        for idx_gate in range(num_gates):
            #calculate gate height and horizon distance
            gate_range: float = (idx_gate + 0.5) * gate_width
            gate_height, gate_horizon_distance = self._calc_height_distance(
                gate_range, sin_elev, cos_elev, radar_height)

            self._data[idx_gate].gate_index = idx_gate
            self._data[idx_gate].gate_mid_height = gate_height
            self._data[idx_gate].horizon_distance = gate_horizon_distance

    def get_closest_to_horizon_distance(self, gate_distance_match: float) -> GeoRefGate:
        """
        Finds and returns the GeoRefGate whose horizon distance is closest to the specified value.

        Uses a binary search approach on the sorted list of horizon distances.

        Args:
            gate_distance_match (float): The target horizon distance to match.

        Returns:
            GeoRefGate: The gate with the closest horizon distance.
        """
        horizon_distances = [gate.horizon_distance for gate in self._data]
        idx = bisect_left(horizon_distances, gate_distance_match)

        if idx <= 0:
            return self._data[0]
        elif idx >= len(self._data):
            return self._data[-1]
        else:
            diff_cur = abs(gate_distance_match - horizon_distances[idx])
            diff_prev = abs(gate_distance_match - horizon_distances[idx - 1])
            return self._data[idx - 1] if diff_prev < diff_cur else self._data[idx]

    def _calc_height_distance(self, gate_range: float, sin_elev: float, cos_elev: float, radar_height: float) -> Tuple[float, float]:
        """
        Calculates the gate height and horizon distance based on the given parameters.

        Args:
            gate_range (float): The range to the middle of the gate.
            sin_elev (float): Sine of the radar elevation angle.
            cos_elev (float): Cosine of the radar elevation angle.
            radar_height (float): The height of the radar.

        Returns:
            Tuple[float, float]: A tuple containing:
                - gate_height (float): The calculated gate height.
                - gate_horizon_distance (float): The calculated horizon distance.
        """
        gate_height: float = radar_height + math.sqrt(GeoReference._EARTH_RADIUS2 +
            gate_range * gate_range +
            2 * GeoReference._EARTH_RADIUS * gate_range * sin_elev) - GeoReference._EARTH_RADIUS
        gate_horizon_distance: float = GeoReference._EARTH_RADIUS * math.asin(
            gate_range * cos_elev / (GeoReference._EARTH_RADIUS + gate_height))

        return gate_height, gate_horizon_distance
    