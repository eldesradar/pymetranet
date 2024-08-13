#!/bin/env python3

#import from system
import sys
import os
import math
import argparse
import time
import numpy as np
from PIL import Image, ImageDraw

#safe pymetranet import
import import_pymetranet
from pymetranet import PolarSweepSerializer, PolarSweep, PolarSweepInfo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    
    for file_name in args.infile:
        #load MSx file
        print("loading file %s..." % file_name)
        loaded_sweep = PolarSweepSerializer.load(file_name)
        print("file %s successfully loaded!" % file_name)

        #create PolarSweepInfo object to get access to some information
        #regarding the loaded MSx sweep file
        sweep_info = PolarSweepInfo(loaded_sweep)
        print("sweep '%s' info" % file_name)
        print("------------------------------")
        print("polarization mode:", sweep_info.get_pol_mode())
        print("wave length: %g" % sweep_info.get_wave_length())
        print("base prf: %g" % sweep_info.get_base_prf())
        print("low prf: %g" % sweep_info.get_low_prf())
        print("high prf: %g" % sweep_info.get_high_prf())
        print("dprf: %d" % sweep_info.get_dprf())
        print("is velocity normalized:", sweep_info.is_velocity_normalized())
        print("velocity nyquist: %g" % sweep_info.get_velocity_nyquist())
        print("is width normalized:", sweep_info.is_width_normalized())
        print("width nyquist: %g" % sweep_info.get_width_nyquist())
        print("is phidp normalized:", sweep_info.is_phidp_normalized())
        print("phidp phase: %g" % sweep_info.get_phidp_phase())
        print("------------------------------")

    return 0

if __name__ == '__main__':
    main()
