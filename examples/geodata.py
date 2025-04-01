#!/bin/env python

#import from system
import sys
import os
import math
import argparse
import time
import numpy as np

#safe pymetranet import
import import_pymetranet
from pymetranet import PolarSweepSerializer, PolarSweep, PolarPpiData, GeoReference, GeoRefGate

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mom", type=str, default="Z")
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    
    for file_name in args.infile:
        print("loading file %s..." % file_name)
        loaded_sweep = PolarSweepSerializer.load(file_name)
        print("file %s successfully loaded" % file_name)
        
        #transform 'mom'
        polar = PolarPpiData()
        polar.transform(loaded_sweep, mom_name=args.mom)
        print("moment '%s' transformed into polar from loaded sweep" % args.mom)

        #get or calculate informazion needed for geo calculation
        gate_width = loaded_sweep.sweepheader.gatewidth
        idx_mid: int = int(len(loaded_sweep.rays) / 2)
        ele_deg_start: float = loaded_sweep.rays[idx_mid].get_startel_deg()
        ele_deg_end: float = loaded_sweep.rays[idx_mid].get_endel_deg()

        print("ele_deg_start '%g' ele_deg_end: '%g'" % (ele_deg_start, ele_deg_end))
        if ele_deg_start > 180.0:
            ele_deg_start = ele_deg_start - 360.0
            print("corrected ele_deg_start to '%g'" % ele_deg_start)
        rad_height: float = loaded_sweep.sweepheader.radarheight * 0.001
        print("gate_width: '%g'" % gate_width)
        print("rad_height: '%g'" % rad_height)

        #build 'geo' i.e. gate height and horizon distance
        #for each gate
        geo_ref: GeoReference = GeoReference()
        geo_ref.build(polar.get_ray(0), ele_deg_start, gate_width, rad_height)

        #print geo information
        for i in range(len(geo_ref.data)):
            geo_info = geo_ref.data[i]
            print("geo info[%03d] gate index: '%g' mid height: '%g' horizon distance: '%g'" \
                  % (i, geo_info.gate_index, geo_info.gate_mid_height, geo_info.horizon_distance))

    return 0

if __name__ == '__main__':
    sys.exit(main())
