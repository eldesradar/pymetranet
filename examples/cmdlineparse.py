#!/bin/env python

#import from system
import sys
import os

#safe pymetranet import
import import_pymetranet
from pymetranet import *

class CappiParams(ProdParamsBase):
    PARAM_FILES = "files"
    PARAM_PID = "pid"
    PARAM_MOMENT = "moment"
    PARAM_TIME = "time"
    PARAM_CURSWEEP = "currentsweep"
    PARAM_VOLSWEEPS = "volumesweeps"
    PARAM_IN_TYPE = "in_type"
    PARAM_HEIGHT = "height"
    PARAM_PSEUDO = "pseudo"
    PARAM_KDPMAX = "kdp_max"
    PARAM_BBCORR = "beam_blockage_corr"
    PARAM_DEACORR = "dealiasing_corr"
    PARAM_FORMAT = "format"
    PARAM_DATABITS = "databits"
    PARAM_SIZE = "size"
    PARAM_COMPRESS = "compress"
    PARAM_ZVPR = "z_vpr"
    PARAM_INDIR = "indir"
    PARAM_OUTDIR = "outdir"
    PARAM_VERBOSE = "verbose"
    PARAM_LINKIT = "linkit"
    PARAM_ENCODING = "encoding"
    PARAM_LINK_NODE_FILE = "link_node_file"
    PARAM_DATA_LEVEL_FILE = "data_level_file"
    PARAM_BLOCK_CORR_FILE = "blockage_corr_file"
    PARAM_SPECKLE = "speckle"
    PARAM_FLT_COEFF = "filter_coefficients"
    PARAM_FLT_LOOPS = "filter_loops"
    PARAM_FLT_THR = "filter_threshold"
    PARAM_FLT_FACTOR = "filter_factor"
    PARAM_REG_WIDTH = "regression_width"
    PARAM_COMMENTS = "comments"
    
    def __init__(self):
        ProdParamsBase.__init__(self)

        #map the fields and info product info defaults, ranges, etc...
        self.init_param_info();
        self.init_product_info();
        
    def init_param_info(self) -> None:
        #set default to values
        self._map_param_info[CappiParams.PARAM_FILES] = ProductParamInfo("", ProductParamType.Hidden)
        self._map_param_info[CappiParams.PARAM_PID] = ProductParamInfo("", ProductParamType.Pid)
        self._map_param_info[CappiParams.PARAM_MOMENT] = ProductParamInfo("Z", ProductParamType.Enum)
        self._map_param_info[CappiParams.PARAM_TIME] = ProductParamInfo("", ProductParamType.Hidden)
        self._map_param_info[CappiParams.PARAM_CURSWEEP] = ProductParamInfo(1, ProductParamType.Hidden)
        self._map_param_info[CappiParams.PARAM_VOLSWEEPS] = ProductParamInfo(1, ProductParamType.Hidden)
        self._map_param_info[CappiParams.PARAM_IN_TYPE] = ProductParamInfo("MSE", ProductParamType.Pid)
        self._map_param_info[CappiParams.PARAM_HEIGHT] = ProductParamInfo(1, ProductParamType.Float)
        self._map_param_info[CappiParams.PARAM_PSEUDO] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_KDPMAX] = ProductParamInfo(28, ProductParamType.Float)
        self._map_param_info[CappiParams.PARAM_BBCORR] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_DEACORR] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_FORMAT] = ProductParamInfo("RECT", ProductParamType.Enum)
        self._map_param_info[CappiParams.PARAM_DATABITS] = ProductParamInfo("8", ProductParamType.Enum)
        self._map_param_info[CappiParams.PARAM_SIZE] = ProductParamInfo(MapSizeRect(400, 400, 1, 1), ProductParamType.MapSizeRect)
        self._map_param_info[CappiParams.PARAM_COMPRESS] = ProductParamInfo(True, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_ZVPR] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_INDIR] = ProductParamInfo("/opt/metraserver/data", ProductParamType.PathDir)
        self._map_param_info[CappiParams.PARAM_OUTDIR] = ProductParamInfo("/opt/metraserver/data", ProductParamType.PathDir)
        self._map_param_info[CappiParams.PARAM_VERBOSE] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_LINKIT] = ProductParamInfo(False, ProductParamType.Bool)
        self._map_param_info[CappiParams.PARAM_ENCODING] = ProductParamInfo("hard-coded", ProductParamType.PathFile)
        self._map_param_info[CappiParams.PARAM_LINK_NODE_FILE] = ProductParamInfo("default", ProductParamType.PathFile)
        self._map_param_info[CappiParams.PARAM_DATA_LEVEL_FILE] = ProductParamInfo("default", ProductParamType.PathFile)
        self._map_param_info[CappiParams.PARAM_BLOCK_CORR_FILE] = ProductParamInfo("default", ProductParamType.PathFile)
        self._map_param_info[CappiParams.PARAM_SPECKLE] = ProductParamInfo(0, ProductParamType.Int)
        self._map_param_info[CappiParams.PARAM_FLT_COEFF] = ProductParamInfo("default", ProductParamType.PathFile)
        self._map_param_info[CappiParams.PARAM_FLT_LOOPS] = ProductParamInfo(10, ProductParamType.Int)
        self._map_param_info[CappiParams.PARAM_FLT_THR] = ProductParamInfo(4.0, ProductParamType.Float)
        self._map_param_info[CappiParams.PARAM_FLT_FACTOR] = ProductParamInfo(1.3, ProductParamType.Float)
        self._map_param_info[CappiParams.PARAM_REG_WIDTH] = ProductParamInfo(10, ProductParamType.Int)
        self._map_param_info[CappiParams.PARAM_COMMENTS] = ProductParamInfo("", ProductParamType.String)
        
    def init_product_info(self) -> None:
        prod_info = self._product_info
        map_info = self._map_param_info
        
        prod_info.product_name = "CAPPI"
        prod_info.version = "Version 2.10.1.0 Apr  8 2024"
        prod_info.description = "The program cappi generates CAPPI product"
        
        #add general group
        group_general = ProductParamGroup("General")
        prod_info.groups.append(group_general)
        
        #add pid to group general
        key = CappiParams.PARAM_PID
        prod_info.params.append(ProductParamPid(key,
            "3-letters as Oxy where x represents the moment, y is the radar ID", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
            
        #add moment
        key = CappiParams.PARAM_MOMENT
        moments = ["W", "V", "UZ", "Z", "ZDR", "RHO", "PHIDP", "KDP"]
        prod_info.params.append(ProductParamEnum(key,
            "moment type for data processing", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value),
            moments, True, True))
            
        #add time
        key = CappiParams.PARAM_TIME
        prod_info.params.append(ProductParamHidden(key,
            "time, priority, compression of input, i.e. 1236523550U", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
            
        #add current sweep
        key = CappiParams.PARAM_CURSWEEP
        prod_info.params.append(ProductParamHidden(key,
            "input sweep number (volume file extension)", group_general,
            str(map_info[key].value), ProductParamDefault[str](True, str(map_info[key].value))))
            
        #add volume sweeps
        key = CappiParams.PARAM_VOLSWEEPS
        prod_info.params.append(ProductParamHidden(key,
            "number of total sweeps (elevations) in volume", group_general,
            str(map_info[key].value), ProductParamDefault[str](True, str(map_info[key].value))))
            
        #add in type
        key = CappiParams.PARAM_IN_TYPE
        prod_info.params.append(ProductParamPid(key,
            "input file type, combined with 'time' to form filename", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
            
        #add height
        key = CappiParams.PARAM_HEIGHT
        prod_info.params.append(ProductParamFloat(key,
            "height for product", group_general,
            map_info[key].value,
            ProductParamDefault[float](True, map_info[key].value),
            ProductParamRange[float](True, 0, 18)))
            
        #add pseudo
        key = CappiParams.PARAM_PSEUDO
        prod_info.params.append(ProductParamBool(key,
            "create pseudo CAPPI", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
            
        #add kdpmax
        key = CappiParams.PARAM_KDPMAX
        prod_info.params.append(ProductParamFloat(key,
            "maximum KDP value (deg/km) in output product", group_general,
            map_info[key].value,
            ProductParamDefault[float](True, map_info[key].value),
            ProductParamRange[float](True, 3, 30)))
            
        #add bb corr
        key = CappiParams.PARAM_BBCORR
        prod_info.params.append(ProductParamBool(key,
            "1 means perform beam blockage correction", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
            
        #add dealiasing correction
        key = CappiParams.PARAM_DEACORR
        prod_info.params.append(ProductParamBool(key,
            "1 means perform dealiasing correction", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
        
        #add format
        key = CappiParams.PARAM_FORMAT
        formats = ["RECT", "POLAR"]
        prod_info.params.append(ProductParamEnum(key,
            "data display format selected from RECT or POLAR", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value),
            formats))
        
        #add databits
        key = CappiParams.PARAM_DATABITS
        databits = ["4", "8"]
        prod_info.params.append(ProductParamEnum(key,
            "data bits 4 or 8", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value),
            databits))
        
        #add size
        key = CappiParams.PARAM_SIZE
        prod_info.params.append(ProductParamMapSizeRect(key,
            "RECT x,y point and resolution (km)", group_general,
            map_info[key].value,
            ProductParamDefault[MapSizeRect](True, map_info[key].value),
            ProductParamRange[MapSizeRect](True,
                MapSizeRect(100, 100, 0.05, 0.05),    #min
                MapSizeRect(1000, 1000, 2.0, 2.0))))  #max
        
        #add compress
        key = CappiParams.PARAM_COMPRESS
        prod_info.params.append(ProductParamBool(key,
            "compress product", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
        
        #add zvpr
        key = CappiParams.PARAM_ZVPR
        prod_info.params.append(ProductParamBool(key,
            "for intensity data, use vpr profile to project data", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
        
        #add indir
        key = CappiParams.PARAM_INDIR
        prod_info.params.append(ProductParamPathDir(key,
            "input data directory", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add outdir
        key = CappiParams.PARAM_OUTDIR
        prod_info.params.append(ProductParamPathDir(key,
            "output data directory", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add verbose
        key = CappiParams.PARAM_VERBOSE
        prod_info.params.append(ProductParamBool(key,
            "verbose flag, 1 for more messages from program", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
        
        #add linkit
        key = CappiParams.PARAM_LINKIT
        prod_info.params.append(ProductParamBool(key,
            "flag 1 for creating link files for product", group_general,
            map_info[key].value, ProductParamDefault[bool](True, map_info[key].value)))
        
        #add encoding
        key = CappiParams.PARAM_ENCODING
        prod_info.params.append(ProductParamPathFile(key,
            "file name which specifies moments encoding", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add link node file
        key = CappiParams.PARAM_LINK_NODE_FILE
        prod_info.params.append(ProductParamPathFile(key,
            "file name which specifies link node directory", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add data level file
        key = CappiParams.PARAM_DATA_LEVEL_FILE
        prod_info.params.append(ProductParamPathFile(key,
            "file name which specifies data levels", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add blockage correction file
        key = CappiParams.PARAM_BLOCK_CORR_FILE
        prod_info.params.append(ProductParamPathFile(key,
            "file name for beam blockage correction, default [installdir]/etc/pgs/blockage_correction_'radarname'.dat", group_general,
            map_info[key].value, ProductParamDefault[str](True, map_info[key].value)))
        
        #add speckle
        key = CappiParams.PARAM_SPECKLE
        prod_info.params.append(ProductParamInt(key,
            "apply speckle fiter", group_general,
            map_info[key].value,
            ProductParamDefault[int](True, map_info[key].value),
            ProductParamRange[int](True, 0, 5)))
        
        #add filter coefficients
        key = CappiParams.PARAM_FLT_COEFF
        prod_info.params.append(ProductParamString(key,
            "file name which specifies coefficients for PHDP FIR filter", group_general,
            map_info[key].value,
            ProductParamDefault[str](True, map_info[key].value)))
        
        #add filter loops
        key = CappiParams.PARAM_FLT_LOOPS
        prod_info.params.append(ProductParamInt(key,
            "number of times for filtering", group_general,
            map_info[key].value,
            ProductParamDefault[int](True, map_info[key].value),
            ProductParamRange[int](True, 0, 20)))
        
        #add filter threshold
        key = CappiParams.PARAM_FLT_THR
        prod_info.params.append(ProductParamFloat(key,
            "threshold to determine more PHDP filtering", group_general,
            map_info[key].value,
            ProductParamDefault[float](True, map_info[key].value),
            ProductParamRange[float](True, 0, 20)))
        
        #add filter factor
        key = CappiParams.PARAM_FLT_FACTOR
        prod_info.params.append(ProductParamFloat(key,
            "factor to change filter threshold", group_general,
            map_info[key].value,
            ProductParamDefault[float](True, map_info[key].value),
            ProductParamRange[float](True, 1, 2)))
        
        #add regression width
        key = CappiParams.PARAM_REG_WIDTH
        prod_info.params.append(ProductParamInt(key,
            "integrating data points to generate KDP", group_general,
            map_info[key].value,
            ProductParamDefault[int](True, map_info[key].value),
            ProductParamRange[int](True, 2, 20)))
        
        #add comments
        key = CappiParams.PARAM_COMMENTS
        prod_info.params.append(ProductParamString(key,
            "comments added by user", group_general,
            map_info[key].value,
            ProductParamDefault[int](True, map_info[key].value)))

def gest_init_args(prog_name: str, args):
    for arg in args:
        if arg == "-init":
            params = CappiParams()
            print("%s %s" % (prog_name, params.get_params_cmd_line()))
            return True
        elif arg == "-xmldef":
            params = CappiParams()
            print("%s" % params.get_xml_def())
            return True
            
    return False
    
def main():
    if gest_init_args("CAPPI", sys.argv):
        return 0
        
    parser = CmdLineParams()
    ret_parse = parser.parse_cmd_line(len(sys.argv), sys.argv)
    
    #usage of get param count method
    #print("##### GET PARAM COUNT METHOD ###")
    #print("param count: %d" % parser.get_params_count())
    
    #usage of params dicitonary
    #print("##### ITERATE PARAM DICTIONARY ###")
    #idx = 0
    #for param_name, param_value in parser.params.items():
        #print("param[%d] - name: '%s' value: '%s'" % (idx, param_name, param_value))
        #idx += 1
        
    #usage of get param value iterating dictionary keys
    #print("##### ITERATE PARAM KEYS AND GETTING PARAM VALUE VIA GET PARAM VALUE METHOD ###")
    #idx = 0
    #for key in parser.params:
        #value = parser.get_param_value(key)
        #print("param[%d] - key: '%s' value(via get_param_value): '%s'" % (idx, key, value))
        #idx += 1
    
    #validate parameters
    params = CappiParams()
    try:
        params.validate(parser)
    except Exception as ex:
        print(ex)
        return 1
        
    #construct parameters for product with its default values, then
    #inject command line inside params
    ret = params.inject(parser);
    print("injected %d parameters from the command line" % ret);
    for param_name, param_value in params.map_info.items():
        print("%s: '%s' (type: %s)" % (param_name, param_value.value, param_value.param_type))

    return 0

if __name__ == '__main__':
    main()
