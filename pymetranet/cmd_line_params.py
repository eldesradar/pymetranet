#!/bin/env python

from enum import IntEnum
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

class CmdLineParams:
    def __init__(self):
        self._cmdline = ""
        self._params = {}
        
    @property
    def params(self) -> Dict[str, str]:
        return self._params
        
    def parse_cmd_line(self, *args):
        """
        Parse the command line.

        This method can be called in two ways:
        1. With argc and argv: parse_cmd_line(argc, argv)
        2. With a single string: parse_cmd_line(cmdLine)

        Args:
            *args: Either (argc, argv) or (cmdLine,)

        Returns:
            int: The number of parameters processed or a value less than
                 zero in case of an error.
        """
        if len(args) == 2:
            argc, argv = args
            
            cmd_line = ''
            for i in range(argc):
                #embrace the param value with double quotes at the beginning
                #and at the end so that argument 'c=3 4 5' become 'c="3 4 5"'
                arg = argv[i]
                index = arg.find('=')
                if index != -1:
                    arg = arg[:index + 1] + '"' + arg[index + 1:] + '"'
                
                #add argument to the cmdLine
                cmd_line += arg
                
                #if this is not the last element, add a space before continuing the loop
                if i + 1 < argc:
                    cmd_line += ' '
                    
            self.cmdline = cmd_line
        elif len(args) == 1:
            self.cmdline = args[0]
        else:
            return -1

        self.params.clear()
        
        if not self.cmdline:
            return -1
            
        start_index = 0
        while True:
            #find ' ' (space) starting from startIndex
            sep_index = self.cmdline.find(' ', start_index)
            if sep_index == -1:
                break
                
            #find '=' starting from sepIndex+1
            eq_index = self.cmdline.find('=', sep_index + 1)
            if eq_index == -1:
                break
                
            #find first \" starting from eqIndex+1
            pos_start = self.cmdline.find('"', eq_index + 1)
            if pos_start == -1:
                break
                
            #find next \" starting from posStart+1
            pos_end = self.cmdline.find('"', pos_start + 1)
            if pos_end == -1:
                break
                
            #get the parameter name and value
            param_name = self.cmdline[sep_index + 1:eq_index]
            param_value = self.cmdline[pos_start + 1:pos_end]
            
            #add the parameter to the vector
            self.params[param_name] = param_value
            
            #update startIndex to search for next parameter
            start_index = pos_end
            
        return len(self.params)

    def get_param_value(self, param_name):
        return self.params.get(param_name, "")

    def get_params_count(self):
        return len(self.params)
        

class ProductParamType(IntEnum):
    Undefined = 0
    Pid = 1
    Hidden = 2
    Bool = 3
    Int = 4
    Float = 5
    String = 6
    Enum = 7
    MapSizeRect = 8
    PathDir = 9
    PathFile = 10
    CatchmentFile = 11
    RadarCfg = 12
    RadarNetwork = 13


class MapSizeRect:
    def __init__(self, x_size: int=0, y_size: int=0, x_res: float=0.0, y_res: float=0.0):
        self._x_size = x_size
        self._y_size = y_size
        self._x_res = x_res
        self._y_res = y_res
        
    @property
    def x_size(self) -> int:
        return self._x_size
        
    @x_size.setter
    def x_size(self, value: int) -> None:
        self._x_size = value
        
    @property
    def y_size(self) -> int:
        return self._y_size
        
    @y_size.setter
    def y_size(self, value: int) -> None:
        self._y_size = value
        
    @property
    def x_res(self) -> float:
        return self._x_res
        
    @x_res.setter
    def x_res(self, value: float) -> None:
        self._x_res = value
        
    @property
    def y_res(self) -> float:
        return self._y_res
        
    @y_res.setter
    def y_res(self, value: float) -> None:
        self._y_res = value
        
        
class ParamBoolConverter:
    @staticmethod
    def to_string(value: bool) -> str:
        return '1' if value else '0'

    @staticmethod
    def from_string(value: str) -> bool:
        return value == '1'

        
class ParamIntConverter:
    @staticmethod
    def to_string(value: int) -> str:
        return str(value)

    @staticmethod
    def from_string(value: str) -> int:
        try:
            return int(value)
        except ValueError:
            return 0


class ParamFloatConverter:
    @staticmethod
    def to_string(value: float) -> str:
        return str(value)

    @staticmethod
    def from_string(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            return 0.0


class ParamStringConverter:
    @staticmethod
    def to_string(value: str) -> str:
        return value

    @staticmethod
    def from_string(value: str) -> str:
        return value


class ParamMapSizeRectConverter:
    @staticmethod
    def to_string(value: MapSizeRect) -> str:
        return f"{value.x_size};{value.y_size};{value.x_res};{value.y_res}"

    @staticmethod
    def from_string(value: str) -> MapSizeRect:
        pos_start = 0
        pos_end = value.find(';', pos_start)
        x_size = ParamIntConverter.from_string(value[:pos_end]) if pos_end != -1 else 0
        pos_start = pos_end + 1
        pos_end = value.find(';', pos_start)
        y_size = ParamIntConverter.from_string(value[pos_start:pos_end]) if pos_end != -1 else 0
        pos_start = pos_end + 1
        pos_end = value.find(';', pos_start)
        x_res = ParamFloatConverter.from_string(value[pos_start:pos_end]) if pos_end != -1 else 0.0
        pos_start = pos_end + 1
        y_res = ParamFloatConverter.from_string(value[pos_start:]) if pos_end != -1 else 0.0
        
        return MapSizeRect(x_size, y_size, x_res, y_res)


class ProductParamGroup:
    def __init__(self, name: str=None):
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name
        
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        
class ProductParam(ABC):
    def __init__(self, name: str, descr: str, param_type: ProductParamType, group: ProductParamGroup):
        self._name = name
        self._descr = descr
        self._param_type = param_type
        self._group = group
        
    @property
    def name(self) -> str:
        return self._name
        
    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def descr(self) -> str:
        return self._descr
        
    @descr.setter
    def descr(self, value: str) -> None:
        self._descr = descr

    @property
    def param_type(self) -> ProductParamType:
        return self._param_type
        
    @param_type.setter
    def param_type(self, value: ProductParamType) -> None:
        self._param_type = value

    @property
    def group(self) -> ProductParamGroup:
        return self._group
        
    @group.setter
    def group(self, value: ProductParamGroup) -> None:
        self._group = value

    @abstractmethod
    def get_string_value(self) -> str:
        """
        Subclasses must implement this method
        """
        pass
        
    @abstractmethod
    def set_string_value(self, value: str) -> None:
        """
        Subclasses must implement this method
        """
        pass


T = TypeVar('T')
class ProductParamDefault(Generic[T]):
    def __init__(self, has_default: bool, default_value: T = None):
        if has_default:
            self._has_default = True
            self._default_value = default_value
        else:
            self.has_default = False
            self.default_value = None
            
    @property
    def has_default(self) -> bool:
        return self._has_default
        
    @has_default.setter
    def has_default(self, value: bool) -> None:
        self._default_value = value

    @property
    def default_value(self) -> T:
        return self._default_value

    @default_value.setter
    def default_value(self, value: T) -> None:
        self._default_value = value


class ProductParamRange(Generic[T]):
    def __init__(self, has_range: bool, min_val: T = None, max_val: T = None):
        if has_range:
            self._has_range = True
            self._min_val = min_val
            self._max_val = max_val
        else:
            self._has_range = False
            self._min_val = None
            self._max_val = None

    @property
    def has_range(self) -> bool:
        return self._has_range

    @property
    def min_val(self) -> T:
        return self._min_val

    @property
    def max_val(self) -> T:
        return self._max_val


class ProductParamHidden(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.Hidden, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)


class ProductParamPid(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.Pid, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)


class ProductParamBool(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: bool, default: ProductParamDefault[bool]):
        ProductParam.__init__(self, name, descr, ProductParamType.Bool, group)
        self._value = value
        self._default = default
        self._child_param_list: List[ProductParam] = []

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, value: bool) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[bool]:
        return self._default
        
    @property
    def child_param_list(self) ->  List[ProductParam]:
        return self._child_param_list

    def get_string_value(self) -> str:
        return ParamBoolConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamBoolConverter.from_string(value)


class ProductParamInt(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: int, default: ProductParamDefault[int], param_range: ProductParamRange[int]):
        ProductParam.__init__(self, name, descr, ProductParamType.Int, group)
        self._value = value
        self._default = default
        self._param_range = param_range

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[int]:
        return self._default

    @property
    def param_range(self) -> ProductParamRange[int]:
        return self._param_range

    def get_string_value(self) -> str:
        return ParamIntConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamIntConverter.from_string(value)


class ProductParamFloat(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: float, default: ProductParamDefault[float], param_range: ProductParamRange[float]):
        ProductParam.__init__(self, name, descr, ProductParamType.Float, group)
        self._value = value
        self._default = default
        self._param_range = param_range

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[float]:
        return self._default

    @property
    def param_range(self) -> ProductParamRange[float]:
        return self._param_range

    def get_string_value(self) -> str:
        return ParamFloatConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamFloatConverter.from_string(value)


class ProductParamString(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.String, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)


class ProductParamEnum(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str,
                 default: ProductParamDefault[str], enum_values: List[str], multi: bool = False,
                 custom: bool = False):
        ProductParam.__init__(self, name, descr, ProductParamType.Enum, group)
        self._value = value
        self._default = default
        self._enum_values = enum_values
        self._multi = multi
        self._custom = custom

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    @property
    def enum_values(self) -> List[str]:
        return self._enum_values

    @property
    def multi(self) -> bool:
        return self._multi
        
    @multi.setter
    def multi(self, value: bool) -> None:
        self._multi = value

    @property
    def custom(self) -> bool:
        return self._custom
        
    @custom.setter
    def custom(self, value: bool) -> None:
        self._custom = value

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)
        
        
class ProductParamMapSizeRect(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: MapSizeRect, default: ProductParamDefault[MapSizeRect], param_range: ProductParamRange[MapSizeRect]):
        ProductParam.__init__(self, name, descr, ProductParamType.MapSizeRect, group)
        self._value = value
        self._default = default
        self._param_range = param_range

    @property
    def value(self) -> MapSizeRect:
        return self._value

    @value.setter
    def value(self, value: MapSizeRect) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[MapSizeRect]:
        return self._default

    @property
    def param_range(self) -> ProductParamRange[MapSizeRect]:
        return self._param_range

    def get_string_value(self) -> str:
        return ParamMapSizeRectConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamMapSizeRectConverter.from_string(value)
        

class ProductParamPathDir(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.PathDir, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)
        

class ProductParamPathFile(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.PathFile, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)
        
        
class ProductParamCatchmentFile(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.CatchmentFile, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)
        

class ProductParamRadarNetwork(ProductParam):
    def __init__(self, name: str, descr: str, group: ProductParamGroup, value: str, default: ProductParamDefault[str]):
        ProductParam.__init__(self, name, descr, ProductParamType.RadarNetwork, group)
        self._value = value
        self._default = default

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def default(self) -> ProductParamDefault[str]:
        return self._default

    def get_string_value(self) -> str:
        return ParamStringConverter.to_string(self._value)
        
    def set_string_value(self, value: str) -> None:
        self._value = ParamStringConverter.from_string(value)
        
        
class ProductInfo:
    def __init__(self, product_name: str=None, version: str=None, descr: str=None):
        self._product_name = product_name
        self._version = version
        self._descr = descr
        self._groups: List[ProductParamGroup] = []
        self._params: List[ProductParam] = []
            
    @property
    def product_name(self) -> str:
        return self._product_name

    @product_name.setter
    def product_name(self, value: str) -> None:
        self._product_name = value
        
    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value
        
    @property
    def description(self) -> str:
        return self._descr

    @description.setter
    def description(self, value: str) -> None:
        self._descr = value
        
    @property
    def groups(self) -> List[ProductParamGroup]:
        return self._groups
        
    @property
    def params(self) -> List[ProductParam]:
        return self._params
        
    def get_param(self, param_name: str) -> ProductParam:
        for param in self._params:
            if param.name == param_name:
                return param
                
        return None


class ProductParamInfo:
    def __init__(self, value=None, param_type: ProductParamType=ProductParamType.Undefined):
        self._value = value
        self._param_type = param_type
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        self._value = value
    
    @property
    def param_type(self) -> ProductParamType:
        return self._param_type;
        
    @param_type.setter
    def param_type(self, value: ProductParamType) -> None:
        self._param_type = value


class ProdParamsBase(ABC):
    def __init__(self):
        self._map_param_info = {}
        self._product_info = ProductInfo()
        
    @property
    def map_info(self) -> Dict[str, ProductParamInfo]:
        return self._map_param_info
        
    @property
    def prod_info(self) -> ProductInfo:
        return self._product_info
    
    def inject(self, cmd_line_params: CmdLineParams) -> int:
        ret_counter = 0
        for name, value in cmd_line_params.params.items():
            info = self.get_param_info(name)
            if info.param_type != ProductParamType.Undefined:
                if info.param_type == ProductParamType.Hidden:
                    #special case for hidden parameters, handle in a hard-coded
                    #way the fields 'time' 'currentsweep' 'volumesweeps' and 'debug'
                    #all the other fields will be handled forcibly as strings
                    if name == "time":
                        info.value = ParamStringConverter.from_string(value)
                        ret_counter += 1
                    elif name in ["currentsweep", "volumesweeps", "debug"]:
                        info.value = ParamIntConverter.from_string(value)
                        ret_counter += 1
                    else:
                        info.value = ParamStringConverter.from_string(value)
                        ret_counter += 1
                elif info.param_type in [ProductParamType.Pid, ProductParamType.String, ProductParamType.Enum,
                        ProductParamType.PathDir, ProductParamType.PathFile,
                        ProductParamType.CatchmentFile, ProductParamType.RadarNetwork,
                        ProductParamType.RadarCfg]:
                    info.value = ParamStringConverter.from_string(value)
                    ret_counter += 1
                         
                elif info.param_type == ProductParamType.Bool:
                    info.value = ParamBoolConverter.from_string(value)
                    ret_counter += 1
                        
                elif info.param_type == ProductParamType.Int:
                    info.value = ParamIntConverter.from_string(value)
                    ret_counter += 1
                        
                elif info.param_type == ProductParamType.Float:
                    info.value = ParamFloatConverter.from_string(value)
                    ret_counter += 1
                        
                elif info.param_type == ProductParamType.MapSizeRect:
                    info.value = ParamMapSizeRectConverter.from_string(value)
                    ret_counter += 1
                        
        return ret_counter
        
    def get_params_cmd_line(self) -> str:
        ret = ""
        
        for name, info in self._map_param_info.items():
            if info.param_type != ProductParamType.Hidden:
                ret += f"{name}=\"{self.get_param_string(info)}\" "
                
        #remove the last space
        return ret[:-1]
    
    def get_xml_def(self) -> str:
        #create root node
        root_node = ET.Element("productdef")
        
        #create node info child of root
        info_node = ET.SubElement(root_node, "info")
        info_node.set("version", self._product_info.version)
        info_node.set("description", self._product_info.description)
        
        #create node params child of root
        params_node = ET.SubElement(root_node, "params")
        
        #create groups nodes children of params
        groups = self._product_info.groups
        params = self._product_info.params
        for group in groups:
            group_node = ET.SubElement(params_node, "group")
            group_node.set("name", group.name)
            
            #create param nodes children of group
            for param in params:
                #skip this param if does not belong to this group
                if param.group.name != group.name:
                    continue
                    
                #add this param to this group
                param_node = ET.SubElement(group_node, "param")
                param_node.set("name", param.name)
                param_node.set("type", self.get_param_type_string(param.param_type))
                param_node.set("default", param.get_string_value())
                
                #it it's an enum parameter add enum values
                #handle multi and custom parameters
                if param.param_type == ProductParamType.Enum:
                    #ppe = param
                    attr_multi = "1" if param.multi else "0"
                    param_node.set("multi", attr_multi)
                    attr_custom = "1" if param.custom else "0"
                    param_node.set("custom", attr_custom)
                    
                #if this parameter has range, add range
                param_min, param_max = self.get_param_range(param)
                if param_min is not None and param_max is not None:
                    param_node.set("range", f"{{{param_min}}}-{{{param_max}}}")
                    
                #add description attribute
                param_node.set("descr", param.descr)
                
                #it it's an enum parameter add enum values
                if param.param_type == ProductParamType.Enum:
                    enum_node = ET.SubElement(param_node, "values")
                    #ppe = param
                    for enum_value in param.enum_values:
                        value_node = ET.SubElement(enum_node, "value")
                        value_node.text = enum_value
        
        xml_str = minidom.parseString(ET.tostring(root_node, encoding='unicode')).toprettyxml(indent="    ")
        #xml_str = xml_str.replace('&lt;', '<').replace('&gt;', '>').replace('><', '>\n<').replace('\t', '    ')
        
        return xml_str
    
    def validate(self, cmd_line_params):
        for param_name, param_value in cmd_line_params.params.items():
            info = self.get_param_info(param_name)
            param = self._product_info.get_param(param_name)
            if info.param_type != ProductParamType.Undefined and param:
                if info.param_type == ProductParamType.Hidden:
                    #special case for hidden parameters, handle in a hard-coded
                    #way the fields 'time' currentsweep' 'volumesweeps' and 'debug'
                    #all the other fields will be handled forcibly as strings
                    if param_name == "time":
                        # TODO: implement custom validation for hidden field time
                        pass
                    elif param_name in ["currentsweep", "volumesweeps", "debug"]:
                        # TODO: implement custom validation for hidden fields
                        pass
                    else:
                        # TODO: implement custom validation for hidden fields
                        pass
                            
                elif info.param_type in [ProductParamType.Pid, ProductParamType.String,
                        ProductParamType.PathDir, ProductParamType.PathFile,
                        ProductParamType.CatchmentFile, ProductParamType.RadarNetwork,
                        ProductParamType.RadarCfg]:
                    #no validation, accept any value
                    pass
                        
                elif info.param_type == ProductParamType.Enum:
                    #implement validation for enum
                    #ppe = param.AsEnum()
                    #if it's not multi and it's not custom param_value
                    #must be equal to one of the possible values
                    if not param.multi and not param.custom:
                        if param_value not in param.enum_values:
                            acceptedValues = "|".join(param.enum_values)
                            raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for enum type. accepted values ({acceptedValues})")
                    
                elif info.param_type == ProductParamType.Bool:
                    #only '0' or '1' are accepted as valid values
                    if param_value not in ["0", "1"]:
                        raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for bool type. accepted values (0|1)")
                    
                elif info.param_type == ProductParamType.Int:
                    #validate string as valid integer number
                    if not re.match(r"^-?\d+$", param_value):
                        raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for int type. not an integer number")
                        
                    #validate range
                    value = int(param_value)
                    #paramInt = param.AsInt()
                    param_range = param.param_range
                    if param_range.has_range:
                        if not is_in_range(value, param_range.val_min, param_range.val_max):
                            str_min, str_max = get_param_range(param)
                            rangeValues = "{%s}-{%s}" % (str_min, str_max)
                            raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for range '{rangeValues}'")
                                
                elif info.param_type == ProductParamType.Float:
                        #validate string as valid float number
                        if not re.match(r"^-?\d+(\.\d*)?$", param_value):
                            raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for float type. not a floating point number")
                                
                        #validate range
                        value = float(param_value)
                        #paramFloat = param.AsFloat()
                        param_range = param.param_range
                        if param_range.has_range:
                            if not is_in_range(value, param_range.val_min, param_range.val_max):
                                str_min, str_max = get_param_range(param)
                                rangeValues = "{%s}-{%s}" % (str_min, str_max)
                                raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for range '{rangeValues}'")
                                
                elif info.param_type == ProductParamType.MapSizeRect:
                    #validate string as valid mapsizerect
                    value = ParamMapSizeRectConverter.FromString(param_value)
                    #paramRect = param
                    param_range = param.param_range
                    if param_range.has_range:
                        if not is_in_range(value.x_size, param_range.val_min.x_size,  param_range.val_max.x_size) or \
                            not IsInRange(value.y_size, param_range.val_min.y_size,  param_range.val_max.y_size) or \
                            not IsInRange(value.x_res, param_range.val_min.x_res,  param_range.val_max.x_res) or \
                            not IsInRange(value.y_res, param_range.val_min.y_res,  param_range.val_max.y_res):
                                str_min, str_max = get_param_range(param)
                                rangeValues = "{%s}-{%s}" % (str_min, str_max)
                                raise ValueError(f"parameter '{param_name}': invalid value '{param_value}' for range '{rangeValues}'")
        
    def get_param_info(self, param_name: str) -> ProductParamInfo:
        ret = self._map_param_info.get(param_name, ProductParamInfo(None, ProductParamType.Undefined))
        return self._map_param_info.get(param_name, ProductParamInfo(None, ProductParamType.Undefined))
        
    def get_param_string(self, param_info):
        if param_info.param_type in [ProductParamType.Pid, ProductParamType.String, ProductParamType.Enum,
                ProductParamType.PathDir, ProductParamType.PathFile,
                ProductParamType.CatchmentFile, ProductParamType.RadarNetwork, 
                ProductParamType.RadarCfg]:
            return ParamStringConverter.to_string(param_info.value)
        elif param_info.param_type == ProductParamType.Bool:
            return ParamBoolConverter.to_string(param_info.value)
        elif param_info.param_type == ProductParamType.Int:
            return ParamIntConverter.to_string(param_info.value)
        elif param_info.param_type == ProductParamType.Float:
            return ParamFloatConverter.to_string(param_info.value)
        elif param_info.param_type == ProductParamType.MapSizeRect:
            return ParamMapSizeRectConverter.to_string(param_info.value)
    
        else:
            return ""

    def get_param_type_string(self, param_type):
        if param_type == ProductParamType.Hidden:
            return "hidden"
        elif param_type == ProductParamType.Pid:
            return "pid"
        elif param_type == ProductParamType.String:
            return "string"
        elif param_type == ProductParamType.Enum:
            return "enum"
        elif param_type == ProductParamType.PathDir:
            return "pathdir"
        elif param_type == ProductParamType.PathFile:
            return "pathfile"
        elif param_type == ProductParamType.CatchmentFile:
            return "catchmentfile"
        elif param_type == ProductParamType.RadarNetwork:
            return "radarnetwork"
        elif param_type == ProductParamType.RadarCfg:
            return "radarcfg"
        elif param_type == ProductParamType.Bool:
            return "bool"
        elif param_type == ProductParamType.Int:
            return "int"
        elif param_type == ProductParamType.Float:
            return "float"
        elif param_type == ProductParamType.MapSizeRect:
            return "mapsizerect"
        else:
            return ""

    def get_param_range(self, param):
        param_type = param.param_type
    
        if param_type in [ProductParamType.Pid, ProductParamType.String, ProductParamType.Enum,
                ProductParamType.PathDir, ProductParamType.PathFile,
                ProductParamType.CatchmentFile, ProductParamType.RadarNetwork,
                ProductParamType.RadarCfg, ProductParamType.Bool]:
            return None, None
        elif param_type == ProductParamType.Int:
            param_range = param.param_range
            if param_range.has_range:
                min_val = ParamIntConverter.to_string(param_range.min_val)
                max_val = ParamIntConverter.to_string(param_range.max_val)
                return min_val, max_val
            else:
                return None, None
        elif param_type == ProductParamType.Float:
            param_range = param.param_range
            if param_range.has_range:
                min_val = ParamFloatConverter.to_string(param_range.min_val)
                max_val = ParamFloatConverter.to_string(param_range.max_val)
                return min_val, max_val
            else:
                return None, None
        elif param_type == ProductParamType.MapSizeRect:
            param_range = param.param_range
            if param_range.has_range:
                min_val = ParamMapSizeRectConverter.to_string(param_range.min_val)
                max_val = ParamMapSizeRectConverter.to_string(param_range.max_val)
                return min_val, max_val
            else:
                return None, None
        else:
            return None, None

    def is_in_range(self, value, val_min, val_max):
        return val_min <= value <= val_max
    
    @abstractmethod
    def init_param_info(self) -> None:
        """
        Subclasses must implement this method
        """
        pass
        
    @abstractmethod
    def init_product_info(self) -> None:
        """
        Subclasses must implement this method
        """
        pass
