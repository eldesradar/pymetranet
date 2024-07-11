#!/bin/env python

#import from system
import sys
import os
import math
import argparse
import numpy as np
from PIL import Image, ImageDraw

#safe pymetranet import
import import_pymetranet
from pymetranet import PolarSweepSerializer, PolarSweep, PolarPpiData

ERADIUS = 6371000.0 * 4.0 / 3.0
EARTH_RADIUS = ERADIUS * 0.001
EARTH_RADIUS2 = EARTH_RADIUS * EARTH_RADIUS
    
def calc_range(gate_range, sin_elev, cos_elev, radar_height):
    global EARTH_RADIUS, EARTH_RADIUS2
    
    gate_height = radar_height + math.sqrt(EARTH_RADIUS2 +
        gate_range * gate_range +
        2 * EARTH_RADIUS * gate_range * sin_elev) - EARTH_RADIUS;
    gate_horizon_distance = EARTH_RADIUS * math.asin(gate_range * cos_elev / (EARTH_RADIUS + gate_height));
    
    return gate_height, gate_horizon_distance
    
def generate_waterfall_image_from_polar(polar: PolarPpiData):
    img_waterfall = Image.new("RGB", (polar.num_gates, polar.num_rays), (255, 255, 255))
    for i in range(polar.num_rays):
        for j in range(polar.num_gates):
            if not math.isnan(polar.data[i][j]):
                img_waterfall.putpixel((j, i), (0, 0, 0))

    return img_waterfall

def generate_rect_image_from_rect(rect: np.ndarray):
    height = rect.shape[0]
    width = rect.shape[1]
    img_rect = Image.new("RGB", (width, height), (255, 255, 255))
    for i in range(height):
        for j in range(width):
            if not math.isnan(rect[i][j]):
                img_rect.putpixel((j, i), (0, 0, 0))

    return img_rect

    #for ray_row in range(polar.num_rays):
            #for gate_col in range(polar.num_gates):
                #if not math.isnan(polar.data[ray_row][gate_col]):
                    #print("data[%03d][%03d]: %g" % (ray_row, gate_col, polar.data[ray_row][gate_col]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mom", type=str, default="Z")
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    
    for file_name in args.infile:
        print("loading file %s..." % file_name)
        loaded_sweep = PolarSweepSerializer.load(file_name)
        print("file %s successfully loaded!" % file_name)
        
        #transform 'mom'
        polar = PolarPpiData()
        polar.transform(loaded_sweep, mom_name=args.mom)
        #print("polar data rays: %d gates: %d" % (polar.num_rays, polar.num_gates))
        #for ray_row in range(polar.num_rays):
            #for gate_col in range(polar.num_gates):
                #if not math.isnan(polar.data[ray_row][gate_col]):
                    #print("data[%03d][%03d]: %g" % (ray_row, gate_col, polar.data[ray_row][gate_col]))
        
        #generate waterfall image from polar
        img_waterfall = generate_waterfall_image_from_polar(polar)
        
        #save waterfall image to disk
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        img_waterfall_path = os.path.join(script_dir, os.path.basename(file_name) + ".waterfall.png")
        img_waterfall.save(img_waterfall_path)
        print("image saved in %s" % img_waterfall_path)

        #generate rect from polar
        gw = loaded_sweep.sweepheader.gatewidth
        rect = polar.polar2rect(gw)
        #print("calculated rect using %d gates with a gate width of %g so resulting " \
            #"with a range of: %gkm" % (polar.num_gates, gw, polar.num_gates * gw))
        #print(rect.shape)
        #print(rect)

        #generate rect image from rect
        img_rect = generate_rect_image_from_rect(rect)

        #save polar image to disk
        img_rect_path = os.path.join(script_dir, os.path.basename(file_name) + ".rect.png")
        img_rect.save(img_rect_path)
        print("image saved in %s" % img_rect_path)

    return 0

if __name__ == '__main__':
    main()
