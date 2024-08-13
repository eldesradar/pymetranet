#!/bin/env python3

import math
from abc import ABC, abstractmethod
import numpy as np
from .cmd_line_params import MapSizeRect

class ProductData(ABC):
    def __init__(self) -> None:
        self._data: np.ndarray = None

    @property
    def data(self) -> np.ndarray:
        return self._data
    
    @data.setter
    def data(self, value: np.ndarray) -> None:
        self._data = value
        
    @property
    @abstractmethod
    def num_rows(self) -> int:
        """
        Subclasses must implement this method
        """
        pass

    @property
    @abstractmethod
    def num_cols(self) -> int:
        """
        Subclasses must implement this method
        """
        pass

class ProductDataPolar(ProductData):
    def __init__(self, num_rays: int, num_gates: int, data: np.ndarray=None) -> None:
        super().__init__()

        self._num_rays: int = num_rays
        self._num_gates: int = num_gates

        if data is None:
            self._data = data
        else:
            #if shape of data is 1d, get len of 1d array and verify
            #congurence with num rays and num gates
            #else if shape of data is 2d, get overall total size
            #of 2d array and verify congruence with num_rays and num gates
            #else if shape is not 1d nor 2d then raise an exception with assert
            assert data.ndim == 1 or data.ndim == 2
            assert data.size == num_rays * num_gates
            if data.ndim == 1:
                self.data = data.reshape(num_rays, num_gates)
            elif data.ndim == 2:
                assert data.shape[0] == num_rays and data.shape[1] == num_gates
                self._data = data

    @property
    def num_rays(self) -> int:
        return self._num_rays
    
    @property
    def num_gates(self) -> int:
        return self._num_gates
    
    @property
    def num_rows(self) -> int:
        return self.num_rays

    @property
    def num_cols(self) -> int:
        return self.num_gates

class ProductDataRect(ProductData):
    def __init__(self, x_size: int, y_size: int, x_res: float, y_res: float, data: np.ndarray=None) -> None:
        super().__init__()

        self._size: MapSizeRect = MapSizeRect(x_size, y_size, x_res, y_res)

        if data is None:
            self._data = data
        else:
            #if shape of data is 1d, get len of 1d array and verify
            #congurence with x and y
            #else if shape of data is 2d, get overall total size
            #of 2d array and verify congruence with x and y
            #else if shape is not 1d nor 2d then raise an exception with assert
            assert data.ndim == 1 or data.ndim == 2
            assert data.size == x_size * y_size
            if data.ndim == 1:
                self.data = data.reshape(y_size, x_size)
            elif data.ndim == 2:
                assert data.shape[0] == y_size and data.shape[1] == x_size
                self._data = data
    
    @property
    def num_rows(self) -> int:
        return self._size.y_size

    @property
    def num_cols(self) -> int:
        return self._size.x_size
    
    def polar2rect(self, polar: ProductDataPolar, gate_width: float, vectorized: bool=True) -> None:
        if vectorized:
            self.__polar2rect_vectorized(polar, gate_width)
        else:
            self.__polar2rect(polar, gate_width)
        
    def __polar2rect(self, polar: ProductDataPolar, gate_width: float) -> None:
        x_res: float = self._size.x_res * self._size.x_res
        y_res: float = self._size.y_res * self._size.y_res
        
        radar_x0: float = (self._size.x_size - 1) * 0.5
        radar_y0: float = (self._size.y_size - 1) * 0.5

        num_gates: int = polar.num_gates
        
        self._data = np.full((self._size.y_size, self._size.x_size), 0, dtype=np.uint8)
        
        for j in range(self._size.y_size):
            y = j -radar_y0
            for i in range(self._size.x_size):
                x = i - radar_x0
                r = math.sqrt(x * x * x_res + y * y * y_res) #in km
                irng = int(r / gate_width + 0.5)
                if irng < num_gates:
                    azimuth = 57.2957795 * math.atan2(x, y)
                    iaz = 180 - int(azimuth)
                    self._data[j, i] = polar._data[iaz, irng]

    def __polar2rect_vectorized(self, polar: ProductDataPolar, gate_width: float) -> None:
        x_res: float = self._size.x_res
        y_res: float = self._size.y_res

        radar_x0: float = (self._size.x_size - 1) * 0.5
        radar_y0: float = (self._size.y_size - 1) * 0.5

        num_gates: int = polar.num_gates

        self._data = np.full((self._size.y_size, self._size.x_size), 0, dtype=np.uint8)

        # Create meshgrid for x and y coordinates
        y_indices, x_indices = np.meshgrid(np.arange(self._size.y_size), np.arange(self._size.x_size), indexing='ij')
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
        self._data[valid_mask] = polar._data[iaz[valid_mask], irng[valid_mask]]

class ProductDataVertLevels(ProductData):
    def __init__(self, num_floats32: int, num_levels: int, data: np.ndarray=None) -> None:
        super().__init__()

        self._num_floats32: int = num_floats32
        self._num_levels: int = num_levels

        #La gestione delle rows / cols del tipo ProductDataVertLevels non va tanto bene.
        #Il problema e' che sono stati concepiti male storicamente i prodotti di profilo
        #verticale come VAD e VVP.
        #Questi dovrebbero avere come numero di righe il numero di livelli e
        #numero di colonne il numero o meglio ancora i byte occupati da ciascuna
        #riga cioe' da ciascun livello. Invece questi prodotti sono stati
        #concepiti per avere come numero di righe il numero di valori di tipo float32
        #presenti in ogni livello, e come colonne il numero di livello.
        #Questo introduce una doppia anomalia che va gestita in modo strano affinche' tutto
        #funzioni. Si decide by design di rappresentare internamente
        #un'unica riga contenete tutti i valori di tutti i livelli a dritto
        #anche se i metodi num_floats32() e num_levels() restituiscono in realta'
        #il numero di valori float di ciascuna struttura e il numero di livelli
        #logicamente corretti.
        if data is None:
            self._data = data
        else:
            assert data.ndim == 1
            assert data.size == num_floats32 * 4 * num_levels
            self.data = data
    
    @property
    def num_floats32(self) -> int:
        return self._num_floats32
    
    @property
    def num_levels(self) -> int:
        return self._num_levels

    @property
    def num_rows(self) -> int:
        return len(self._data.shape)

    @property
    def num_cols(self) -> int:
        return len(self._size)

