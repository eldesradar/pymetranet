#!/bin/env python3

from enum import IntEnum
from typing import List
import numpy as np
from .product_data import ProductData, ProductDataPolar, ProductDataRect, ProductDataVertLevels
from .lzw15 import decompress as lzw15_decompress, compress as lzw15_compress

class ProductTable:
    def __init__(self, name: str=None, size: int = 0, data=None) -> None:
        self._name: str = name
        self._size: int = size
        self._data: np.ndarray = data

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int) -> None:
        self._size = value
    
    @property
    def data(self) -> np.ndarray:
        return self._data
    
    @data.setter
    def data(self, value) -> None:
        self._data = value
        
class ProductDataType(IntEnum):
    Unknown = 0
    Polar = 1
    Rect = 2
    VertLevels = 3
    #Vad, Vvp, Rhi, etc...

class ProductFile:
    def __init__(self) -> None:
        self._data_type: ProductDataType = ProductDataType.Unknown
        self._data: ProductData = None
        self._file_name: str = None
        self._header_info: list = []
        self._tables: List[ProductTable] = []
        self._error_descr = None

    @property
    def data_type(self) -> ProductDataType:
        return self._data_type
    
    @property
    def data(self) -> ProductData:
        return self._data

    @data.setter
    def data(self, value: ProductData) -> None:
        self._data = value
    
    def load_file(self, file_name: str) -> None:
        self._file_name = file_name

        #cleanup internal data
        self._data_type = ProductDataType.Unknown
        self._header_info.clear()
        self._tables.clear()
        self._data = None

        #read product line by line until line 'end_header' is reached
        line: str = ""
        f = open(self._file_name, "rb")
        try:
            while line != "end_header":
                line = f.readline().decode("utf-8")
                line = line.rstrip()
                index = line.find("=")
                if index != -1:
                    name = line[0:index]
                    value = line[index+1:]

                    #search in _header_info if this key already exists
                    #if it exists saerch in a loop if there is a key with the name
                    #adding an incremental counter at the end of the name.
                    #example: 'table_name' is read. Does 'table_name' exist? If it doesn't
                    #add it to _header_info with the name 'table_name'. If later another
                    #'table_name' is read from the file we search in _header_info a key with
                    #'the name 'table_name2', if it doesn't exist, add it as 'table_name2' as name.
                    #then we go forward with this logic with 'table_name3', 'table_name4' and so on...
                    key = self.__get_valid_key_name(name)
                    self._header_info.append([key, value])
        except EOFError as ex:
            f.close()
            raise IOError("unexpected eof found while reading text header")
        
        #set product data type
        if self.__is_vad() or self.__is_vvp() or self.__is_vpr():
            self._data_type = ProductDataType.VertLevels
        else:
            format = self.find_header_info_value("format")
            if format == "RECT" or format == "STORM":
                self._data_type = ProductDataType.Rect
            elif format == "POLAR":
                self._data_type = ProductDataType.Polar

        #read product tables
        num_tables: int = int(self.find_header_info_value("table_num"))
        for count in range(1, num_tables + 1):
            key_table_name: str = "table_name" if count == 1 else "table_name" + str(count)
            key_table_size: str = "table_size" if count == 1 else "table_size" + str(count)
            table_name: str = self.find_header_info_value(key_table_name)
            table_size: int = int(self.find_header_info_value(key_table_size))

            #create a new empty product table inside _tables
            table = ProductTable(table_name, table_size)

            #read data from file into table
            table.data = np.fromfile(f, np.uint8, table.size)

            #add table to list of tables
            self._tables.append(table)

        #read data
        zip_size: int = int(self.find_header_info_value("compressed_bytes"))
        unzip_size: int = int(self.find_header_info_value("uncompressed_bytes"))
        buff_size: int = zip_size if zip_size != 0 else unzip_size

        #uncompress if necessary
        if zip_size != 0 and zip_size != unzip_size:
            buffer = f.read(buff_size)
            ret_buffer_lzw15 = lzw15_decompress(buffer)
            decoded = b"".join(ret_buffer_lzw15)
            buffer = np.frombuffer(decoded, dtype=np.uint8)
        else:
            buffer = np.fromfile(f, np.uint8, buff_size)

        #close the file
        f.close()

        #reshape data read into a 2d matrix and store inside internal _data
        if self._data_type == ProductDataType.Polar:
            num_rays: int = int(self.find_header_info_value("row"))
            num_gates: int = int(self.find_header_info_value("column"))
            #create self._data as a ProductDataPolar object, here
            #buffer is a 1D array but inside the constructor of ProductDataPolar
            #it will be reshaped to be a 2D array with num_rays rows and num_gates cols
            self._data = ProductDataPolar(num_rays, num_gates, buffer)
        elif self._data_type == ProductDataType.Rect:
            x: int = int(self.find_header_info_value("column"))
            y: int = int(self.find_header_info_value("row"))
            xres: float = float(self.find_header_info_value("rect_xres"))
            yres: float = float(self.find_header_info_value("rect_yres"))
            #create self._data as a ProductDataRect object, here
            #buffer is a 1D array but inside the constructor of ProductDataRect
            #it will be reshaped to be a 2D array with y rows and x cols
            self._data = ProductDataRect(x, y, xres, yres, buffer)
        elif self._data_type == ProductDataType.VertLevels:
            num_floats32: int = int(self.find_header_info_value("row"))
            num_levels: int = int(self.find_header_info_value("column"))
            #create self._data as a ProductDataVertLevels
            self._data = ProductDataVertLevels(num_floats32, num_levels, buffer)

    def save_file(self, file_name: str, compress: bool=True) -> None:
        #compressed_bytes and uncompressed_bytes parameters must be present
        info_compressed = self.find_header_info("compressed_bytes")
        if info_compressed is None:
            raise IOError("can't find compressed_bytes info in header")
        info_uncompressed = self.find_header_info("uncompressed_bytes")
        if info_uncompressed is None:
            raise IOError("can't find info_uncompressed info in header")
        
        #compress data if compression is enabled
        buff_size: int = self._data.num_rows * self._data.num_cols
        zip_buff = None
        zip_size = 0
        if compress:
            buff = self._data.data.tobytes()
            compressed = lzw15_compress(buff)
            zip_buff = b"".join(compressed)
            zip_size = len(zip_buff)
            if zip_size <= 0 or zip_size > buff_size:
                raise IOError("error during compression of product data")
            info_compressed[1] = str(zip_size)
        else:
            info_compressed[1] = "0"

        buff_size: int = self._data.num_rows * self._data.num_cols
        info_uncompressed[1] = str(buff_size)

        #openm file for binary writing
        self._file_name = file_name
        f = open(self._file_name, "wb")

        #save header info
        for name, value in self._header_info:
            key: str = self.__normalize_key_name_for_save(name)
            line: str = "%s=%s\n" % (key, value)
            f.write(line.encode())
        f.write("end_header\n".encode())

        #save tables
        for table in self._tables:
            table.data.tofile(f)

        #save data
        if compress and zip_buff is not None and zip_size > 0:
            f.write(zip_buff)
        else:
            self._data.data.tofile(f)

        f.close()

    def get_header_info(self) -> list:
        return self._header_info

    def get_tables(self) -> list:
        return self._tables

    def get_table(self, table_name: str):
        ret_table = [x for x in self._tables if x.name == table_name]
        return ret_table[0] if len(ret_table) > 0 else None
    
    def add_table(self, table_name: str) -> ProductTable:
        new_table = ProductTable(table_name)
        self._tables.append(new_table)
        return new_table

    def add_header_info(self, name: str, value: str):
        info = self.find_header_info(name)
        if info is not None:
            raise ValueError("can't add header info '%s': an info with that name is already present" % name)
        
        self._header_info.append([name, value])

    def find_header_info(self, search: str):
        list = [x for x in self._header_info if x[0] == search]
        return list[0] if len(list) > 0 else None

    def find_header_info_value(self, search: str) -> str:
        info = self.find_header_info(search)
        return None if info is None else info[1]

    def find_header_param_value(self, search: str):
        #get number of params
        info = self.find_header_info("param_num")
        if info is None:
            return None
        
        num_params: int =  int(info[1])
        #iterate all the params searching for 'search'
        for i in range(1, num_params + 1):
            key_param_name: str = "param_name" if i == 1 else "param_name" + str(i)
            param_name: str = self.find_header_info_value(key_param_name)
            if param_name == search:
                key_param_value: str = "param_value" if i == 1 else "param_value" + str(i)
                return self.find_header_info_value(key_param_value)

    def get_file_name(self):
        return self._file_name

    def __get_valid_key_name(self, key: str):
        count: int = 1
        while True:
            search: str = key if count == 1 else key + str(count)
            if len([x for x in self._header_info if x[0] == search]) == 0:
                return search
            count += 1

    def __normalize_key_name_for_save(self, key: str):
        keys_list = ["table_name", "table_size", "param_name", "param_value"]
        for item in keys_list:
            if key.startswith(item):
                return item
            
        return key


    def __is_vad(self):
        pid = self.find_header_info_value("pid")
        if pid[0] == 'V' and pid[1] == 'A':
            return True
        
        format = self.find_header_info_value("format")
        if format == "VADSTR":
            return True
        
        return False

    def __is_vvp(self):
        pid = self.find_header_info_value("pid")
        if pid[0] == 'V' and pid[1] == 'V':
            return True
        
        format = self.find_header_info_value("format")
        if format == "VVPSTR":
            return True
        
        return False

    def __is_vpr(self):
        pid = self.find_header_info_value("pid")
        if pid[0] == 'Z' and pid[1] == 'Z':
            return True
        
        return False