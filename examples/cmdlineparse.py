#!/bin/env python3

#import from system
import sys
import os

#safe pymetranet import
import import_pymetranet
import pymetranet as met

class CappiParams(met.ProdParamsBase):
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
        super().__init__()

        #map the fields and info product info defaults, ranges, etc...
        self.init_param_info()
        self.init_product_info()
        
    def init_param_info(self) -> None:
        #set default to values
        CP = CappiParams
        PPInfo = met.ProductParamInfo
        PPType = met.ProductParamType
        self._map_param_info[CP.PARAM_FILES] = PPInfo("", PPType.Hidden)
        self._map_param_info[CP.PARAM_PID] = PPInfo("", PPType.Pid)
        self._map_param_info[CP.PARAM_MOMENT] = PPInfo("Z", PPType.Enum)
        self._map_param_info[CP.PARAM_TIME] = PPInfo("", PPType.Hidden)
        self._map_param_info[CP.PARAM_CURSWEEP] = PPInfo(1, PPType.Hidden)
        self._map_param_info[CP.PARAM_VOLSWEEPS] = PPInfo(1, PPType.Hidden)
        self._map_param_info[CP.PARAM_IN_TYPE] = PPInfo("MSE", PPType.Pid)
        self._map_param_info[CP.PARAM_HEIGHT] = PPInfo(1, PPType.Float)
        self._map_param_info[CP.PARAM_PSEUDO] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_KDPMAX] = PPInfo(28, PPType.Float)
        self._map_param_info[CP.PARAM_BBCORR] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_DEACORR] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_FORMAT] = PPInfo("RECT", PPType.Enum)
        self._map_param_info[CP.PARAM_DATABITS] = PPInfo("8", PPType.Enum)
        self._map_param_info[CP.PARAM_SIZE] = PPInfo(met.MapSizeRect(400, 400, 1, 1), PPType.MapSizeRect)
        self._map_param_info[CP.PARAM_COMPRESS] = PPInfo(True, PPType.Bool)
        self._map_param_info[CP.PARAM_ZVPR] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_INDIR] = PPInfo("/opt/metraserver/data", PPType.PathDir)
        self._map_param_info[CP.PARAM_OUTDIR] = PPInfo("/opt/metraserver/data", PPType.PathDir)
        self._map_param_info[CP.PARAM_VERBOSE] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_LINKIT] = PPInfo(False, PPType.Bool)
        self._map_param_info[CP.PARAM_ENCODING] = PPInfo("hard-coded", PPType.PathFile)
        self._map_param_info[CP.PARAM_LINK_NODE_FILE] = PPInfo("default", PPType.PathFile)
        self._map_param_info[CP.PARAM_DATA_LEVEL_FILE] = PPInfo("default", PPType.PathFile)
        self._map_param_info[CP.PARAM_BLOCK_CORR_FILE] = PPInfo("default", PPType.PathFile)
        self._map_param_info[CP.PARAM_SPECKLE] = PPInfo(0, PPType.Int)
        self._map_param_info[CP.PARAM_FLT_COEFF] = PPInfo("default", PPType.PathFile)
        self._map_param_info[CP.PARAM_FLT_LOOPS] = PPInfo(10, PPType.Int)
        self._map_param_info[CP.PARAM_FLT_THR] = PPInfo(4.0, PPType.Float)
        self._map_param_info[CP.PARAM_FLT_FACTOR] = PPInfo(1.3, PPType.Float)
        self._map_param_info[CP.PARAM_REG_WIDTH] = PPInfo(10, PPType.Int)
        self._map_param_info[CP.PARAM_COMMENTS] = PPInfo("", PPType.String)
        
    def init_product_info(self) -> None:
        prod_info = self._product_info
        map_info = self._map_param_info
        
        prod_info.product_name = "CAPPI"
        prod_info.version = "Version 2.10.1.0 Apr  8 2024"
        prod_info.description = "The program cappi generates CAPPI product"

        #define some shortcuts to easily create types
        DEF_STR = lambda value : met.ProductParamDefault[str](True, value)
        DEF_BOOL = lambda value : met.ProductParamDefault[bool](True, value)
        DEF_INT = lambda value : met.ProductParamDefault[int](True, value)
        DEF_FLOAT = lambda value : met.ProductParamDefault[float](True, value)
        RNG_INT = lambda val_min, val_max : met.ProductParamRange[int](True, val_min, val_max)
        RNG_FLOAT = lambda val_min, val_max : met.ProductParamRange[float](True, val_min, val_max)
        RNG_SIZE = lambda val_min, val_max : met.ProductParamRange[met.MapSizeRect](True, val_min, val_max)

        
        #add general group
        group_general = met.ProductParamGroup("General")
        prod_info.groups.append(group_general)
        
        #add pid to group general
        key = CappiParams.PARAM_PID
        prod_info.params.append(met.ProductParamPid(key,
            "3-letters as Oxy where x represents the moment, y is the radar ID", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
            
        #add moment
        key = CappiParams.PARAM_MOMENT
        moments = ["W", "V", "UZ", "Z", "ZDR", "RHO", "PHIDP", "KDP"]
        prod_info.params.append(met.ProductParamEnum(key,
            "moment type for data processing", group_general,
            map_info[key].value, DEF_STR(map_info[key].value),
            moments, True, True))
            
        #add time
        key = CappiParams.PARAM_TIME
        prod_info.params.append(met.ProductParamHidden(key,
            "time, priority, compression of input, i.e. 1236523550U", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
            
        #add current sweep
        key = CappiParams.PARAM_CURSWEEP
        prod_info.params.append(met.ProductParamHidden(key,
            "input sweep number (volume file extension)", group_general,
            str(map_info[key].value), DEF_STR(str(map_info[key].value))))
            
        #add volume sweeps
        key = CappiParams.PARAM_VOLSWEEPS
        prod_info.params.append(met.ProductParamHidden(key,
            "number of total sweeps (elevations) in volume", group_general,
            str(map_info[key].value), DEF_STR(str(map_info[key].value))))
            
        #add in type
        key = CappiParams.PARAM_IN_TYPE
        prod_info.params.append(met.ProductParamPid(key,
            "input file type, combined with 'time' to form filename", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add height
        key = CappiParams.PARAM_HEIGHT
        prod_info.params.append(met.ProductParamFloat(key,
            "height for product", group_general,
            map_info[key].value,
            DEF_FLOAT(map_info[key].value),
            RNG_FLOAT(0, 18)))
            
        #add pseudo
        key = CappiParams.PARAM_PSEUDO
        prod_info.params.append(met.ProductParamBool(key,
            "create pseudo CAPPI", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
            
        #add kdpmax
        key = CappiParams.PARAM_KDPMAX
        prod_info.params.append(met.ProductParamFloat(key,
            "maximum KDP value (deg/km) in output product", group_general,
            map_info[key].value,
            DEF_FLOAT(map_info[key].value),
            RNG_FLOAT(3, 30)))
            
        #add bb corr
        key = CappiParams.PARAM_BBCORR
        prod_info.params.append(met.ProductParamBool(key,
            "1 means perform beam blockage correction", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
            
        #add dealiasing correction
        key = CappiParams.PARAM_DEACORR
        prod_info.params.append(met.ProductParamBool(key,
            "1 means perform dealiasing correction", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
        
        #add format
        key = CappiParams.PARAM_FORMAT
        formats = ["RECT", "POLAR"]
        prod_info.params.append(met.ProductParamEnum(key,
            "data display format selected from RECT or POLAR", group_general,
            map_info[key].value, DEF_STR(map_info[key].value),
            formats))
        
        #add databits
        key = CappiParams.PARAM_DATABITS
        databits = ["4", "8"]
        prod_info.params.append(met.ProductParamEnum(key,
            "data bits 4 or 8", group_general,
            map_info[key].value, DEF_STR(map_info[key].value),
            databits))
        
        #add size
        key = CappiParams.PARAM_SIZE
        prod_info.params.append(met.ProductParamMapSizeRect(key,
            "RECT x,y point and resolution (km)", group_general,
            map_info[key].value,
            met.ProductParamDefault[met.MapSizeRect](True, map_info[key].value),
            RNG_SIZE(met.MapSizeRect(100, 100, 0.05, 0.05),    #min
                     met.MapSizeRect(1000, 1000, 2.0, 2.0))))  #max
        
        #add compress
        key = CappiParams.PARAM_COMPRESS
        prod_info.params.append(met.ProductParamBool(key,
            "compress product", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
        
        #add zvpr
        key = CappiParams.PARAM_ZVPR
        prod_info.params.append(met.ProductParamBool(key,
            "for intensity data, use vpr profile to project data", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
        
        #add indir
        key = CappiParams.PARAM_INDIR
        prod_info.params.append(met.ProductParamPathDir(key,
            "input data directory", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add outdir
        key = CappiParams.PARAM_OUTDIR
        prod_info.params.append(met.ProductParamPathDir(key,
            "output data directory", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add verbose
        key = CappiParams.PARAM_VERBOSE
        prod_info.params.append(met.ProductParamBool(key,
            "verbose flag, 1 for more messages from program", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
        
        #add linkit
        key = CappiParams.PARAM_LINKIT
        prod_info.params.append(met.ProductParamBool(key,
            "flag 1 for creating link files for product", group_general,
            map_info[key].value, DEF_BOOL(map_info[key].value)))
        
        #add encoding
        key = CappiParams.PARAM_ENCODING
        prod_info.params.append(met.ProductParamPathFile(key,
            "file name which specifies moments encoding", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add link node file
        key = CappiParams.PARAM_LINK_NODE_FILE
        prod_info.params.append(met.ProductParamPathFile(key,
            "file name which specifies link node directory", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add data level file
        key = CappiParams.PARAM_DATA_LEVEL_FILE
        prod_info.params.append(met.ProductParamPathFile(key,
            "file name which specifies data levels", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add blockage correction file
        key = CappiParams.PARAM_BLOCK_CORR_FILE
        prod_info.params.append(met.ProductParamPathFile(key,
            "file name for beam blockage correction, default [installdir]/etc/pgs/blockage_correction_'radarname'.dat", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))
        
        #add speckle
        key = CappiParams.PARAM_SPECKLE
        prod_info.params.append(met.ProductParamInt(key,
            "apply speckle fiter", group_general,
            map_info[key].value,
            DEF_INT(map_info[key].value),
            RNG_INT(0, 5)))
        
        #add filter coefficients
        key = CappiParams.PARAM_FLT_COEFF
        prod_info.params.append(met.ProductParamString(key,
            "file name which specifies coefficients for PHDP FIR filter", group_general,
            map_info[key].value,
            DEF_STR(map_info[key].value)))
        
        #add filter loops
        key = CappiParams.PARAM_FLT_LOOPS
        prod_info.params.append(met.ProductParamInt(key,
            "number of times for filtering", group_general,
            map_info[key].value,
            DEF_INT(map_info[key].value),
            RNG_INT(0, 20)))
        
        #add filter threshold
        key = CappiParams.PARAM_FLT_THR
        prod_info.params.append(met.ProductParamFloat(key,
            "threshold to determine more PHDP filtering", group_general,
            map_info[key].value,
            DEF_FLOAT(map_info[key].value),
            RNG_FLOAT(0, 20)))
        
        #add filter factor
        key = CappiParams.PARAM_FLT_FACTOR
        prod_info.params.append(met.ProductParamFloat(key,
            "factor to change filter threshold", group_general,
            map_info[key].value,
            DEF_FLOAT(map_info[key].value),
            RNG_FLOAT(1, 2)))
        
        #add regression width
        key = CappiParams.PARAM_REG_WIDTH
        prod_info.params.append(met.ProductParamInt(key,
            "integrating data points to generate KDP", group_general,
            map_info[key].value,
            DEF_INT(map_info[key].value),
            RNG_INT(2, 20)))
        
        #add comments
        key = CappiParams.PARAM_COMMENTS
        prod_info.params.append(met.ProductParamString(key,
            "comments added by user", group_general,
            map_info[key].value, DEF_STR(map_info[key].value)))

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
        
    parser = met.CmdLineParams()
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
    ret = params.inject(parser)
    print("injected %d parameters from the command line" % ret)
    for param_name, param_value in params.map_info.items():
        print("%s: '%s' (type: %s)" % (param_name, param_value.value, param_value.param_type))

    return 0

if __name__ == '__main__':
    main()
