#!/bin/env python3

import math
from abc import ABC, abstractmethod
import numpy as np
from .cmd_line_params import MapSizeRect

class ProductData(ABC):
    """
    Abstract base class for product data.

    This class defines the interface for product data objects, including a NumPy array to hold the data.
    Subclasses must implement the properties `num_rows` and `num_cols`.

    Attributes:
        _data (np.ndarray): The underlying data array.
    """
    def __init__(self) -> None:
        """
        Initializes a new instance of ProductData.
        """
        self._data: np.ndarray = None

    @property
    def data(self) -> np.ndarray:
        """
        Gets the data array.

        Returns:
            np.ndarray: The underlying data array.
        """
        return self._data
    
    @data.setter
    def data(self, value: np.ndarray) -> None:
        """
        Sets the data array.

        Args:
            value (np.ndarray): The new data array.
        """
        self._data = value
        
    @property
    @abstractmethod
    def num_rows(self) -> int:
        """
        Returns the number of rows in the data array.

        Must be implemented by subclasses.

        Returns:
            int: The number of rows.
        """
        pass

    @property
    @abstractmethod
    def num_cols(self) -> int:
        """
        Returns the number of columns in the data array.

        Must be implemented by subclasses.

        Returns:
            int: The number of columns.
        """
        pass

class ProductDataPolar(ProductData):
    """
    Represents polar product data.

    This class stores polar sweep data arranged in a 2D array with dimensions (num_rays x num_gates).
    It ensures that the provided data array matches the expected size and reshapes it if necessary.

    Attributes:
        _num_rays (int): The number of rays.
        _num_gates (int): The number of gates.
    """
    def __init__(self, num_rays: int, num_gates: int, data: np.ndarray=None) -> None:
        """
        Initializes a new ProductDataPolar object.

        Args:
            num_rays (int): The number of rays.
            num_gates (int): The number of gates.
            data (np.ndarray, optional): The data array. If provided, it must have a total size of num_rays * num_gates.
                                         If the array is 1D, it will be reshaped; if it is 2D, its shape is verified.
        """
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
        """
        Returns the number of rays.

        Returns:
            int: The number of rays.
        """
        return self._num_rays
    
    @property
    def num_gates(self) -> int:
        """
        Returns the number of gates.

        Returns:
            int: The number of gates.
        """
        return self._num_gates
    
    @property
    def num_rows(self) -> int:
        """
        Returns the number of rows, which is equal to the number of rays.

        Returns:
            int: The number of rays.
        """
        return self.num_rays

    @property
    def num_cols(self) -> int:
        """
        Returns the number of columns, which is equal to the number of gates.

        Returns:
            int: The number of gates.
        """
        return self.num_gates

class ProductDataRect(ProductData):
    """
    Represents rectangular product data.

    This class stores rectangular product data along with spatial resolution parameters.
    It verifies that the input data matches the expected dimensions and reshapes it if necessary.

    Attributes:
        _size (MapSizeRect): The map size and resolution parameters.
    """
    def __init__(self, x_size: int, y_size: int, x_res: float, y_res: float, data: np.ndarray=None) -> None:
        """
        Initializes a new ProductDataRect object.

        Args:
            x_size (int): The number of columns (width).
            y_size (int): The number of rows (height).
            x_res (float): The resolution in the x-direction.
            y_res (float): The resolution in the y-direction.
            data (np.ndarray, optional): The data array. If provided, its total size must equal x_size * y_size.
        """
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
        """
        Returns the number of rows.

        Returns:
            int: The number of rows.
        """
        return self._size.y_size

    @property
    def num_cols(self) -> int:
        """
        Returns the number of columns.

        Returns:
            int: The number of columns.
        """
        return self._size.x_size
    
    def polar2rect(self, polar: ProductDataPolar, gate_width: float, vectorized: bool=True) -> None:
        """
        Converts polar product data to rectangular (Cartesian) coordinates.

        If 'size' is not specified, it automatically determines a square size (num_gates*2 x num_gates*2),
        with x and y resolutions equal to gate_width.

        Args:
            polar (ProductDataPolar): The polar product data to convert.
            gate_width (float): The width of each gate.
            vectorized (bool, optional): If True, uses the vectorized conversion method; otherwise, uses a loop-based method.
                                         Defaults to True.

        Returns:
            np.ndarray: The rectangular data matrix.
        """
        if vectorized:
            self.__polar2rect_vectorized(polar, gate_width)
        else:
            self.__polar2rect(polar, gate_width)
        
    def __polar2rect(self, polar: ProductDataPolar, gate_width: float) -> None:
        """
        Converts polar data to rectangular coordinates using a loop-based approach.

        Args:
            polar (ProductDataPolar): The polar product data.
            gate_width (float): The width of each gate.

        Returns:
            np.ndarray: The rectangular data matrix.
        """
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
        """
        Converts polar data to rectangular coordinates using a vectorized approach.

        Args:
            polar (ProductDataPolar): The polar product data.
            gate_width (float): The width of each gate.

        Returns:
            np.ndarray: The rectangular data matrix.
        """
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
    """
    Represents vertical levels product data.

    This class is designed for vertical profile products (e.g., VAD, VVP).
    Due to historical design decisions, the internal representation may differ
    from the logical number of levels and float32 values per level.

    Attributes:
        _num_floats32 (int): Number of float32 values per level (as stored).
        _num_levels (int): Logical number of levels.
    """
    def __init__(self, num_floats32: int, num_levels: int, data: np.ndarray=None) -> None:
        """
        Initializes a new ProductDataVertLevels object.

        Args:
            num_floats32 (int): The number of float32 values per level.
            num_levels (int): The logical number of vertical levels.
            data (np.ndarray, optional): The data array. Must be 1D with size equal to num_floats32 * 4 * num_levels.
        """
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
        """
        Returns the number of float32 values per level.

        Returns:
            int: The number of float32 values.
        """
        return self._num_floats32
    
    @property
    def num_levels(self) -> int:
        """
        Returns the logical number of vertical levels.

        Returns:
            int: The number of vertical levels.
        """
        return self._num_levels

    @property
    def num_rows(self) -> int:
        """
        Returns the number of rows in the data representation.

        Note: Due to historical design, this may not directly represent the logical number of levels.

        Returns:
            int: The number of rows.
        """
        return len(self._data.shape)

    @property
    def num_cols(self) -> int:
        """
        Returns the number of columns in the data representation.

        Note: Due to historical design, this may not directly represent the logical number of levels.

        Returns:
            int: The number of columns.
        """
        return len(self._size)

