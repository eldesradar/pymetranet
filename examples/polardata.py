#!/bin/env python

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
from pymetranet import PolarSweepSerializer, PolarSweep, PolarPpiData

ERADIUS = 6371000.0 * 4.0 / 3.0
EARTH_RADIUS = ERADIUS * 0.001
EARTH_RADIUS2 = EARTH_RADIUS * EARTH_RADIUS
    
def calc_range(gate_range, sin_elev, cos_elev, radar_height):
    global EARTH_RADIUS, EARTH_RADIUS2
    
    gate_height = radar_height + math.sqrt(EARTH_RADIUS2 +
        gate_range * gate_range +
        2 * EARTH_RADIUS * gate_range * sin_elev) - EARTH_RADIUS
    gate_horizon_distance = EARTH_RADIUS * math.asin(gate_range * cos_elev / (EARTH_RADIUS + gate_height))
    
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mom", type=str, default="Z")
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    
    for file_name in args.infile:
        print("loading file %s..." % file_name)
        t_start = time.perf_counter()
        loaded_sweep = PolarSweepSerializer.load(file_name)
        t_stop = time.perf_counter()
        print("file %s successfully loaded in %.3f secs." % (file_name, t_stop-t_start))
        
        #transform 'mom'
        t_start = time.perf_counter()
        polar = PolarPpiData()
        polar.transform(loaded_sweep, mom_name=args.mom)
        t_stop = time.perf_counter()
        print("moment '%s' transformed into polar from loaded sweep in in %.3f secs." % (args.mom, t_stop-t_start))
        #print("polar data rays: %d gates: %d" % (polar.num_rays, polar.num_gates))
        #for ray_row in range(polar.num_rays):
            #for gate_col in range(polar.num_gates):
                #if not math.isnan(polar.data[ray_row][gate_col]):
                    #print("data[%03d][%03d]: %g" % (ray_row, gate_col, polar.data[ray_row][gate_col]))
        
        #generate waterfall image from polar object
        t_start = time.perf_counter()
        img_waterfall = generate_waterfall_image_from_polar(polar)
        t_stop = time.perf_counter()
        print("waterfall image from polar generated in %.3f secs." % (t_stop-t_start))
        
        #save waterfall image to disk
        t_start = time.perf_counter()
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        img_waterfall_path = os.path.join(script_dir, os.path.basename(file_name) + ".waterfall.png")
        img_waterfall.save(img_waterfall_path)
        t_stop = time.perf_counter()
        print("waterfall image saved in %s in %.3f secs." % (img_waterfall_path, t_stop-t_start))

        #generate rect from polar
        t_start = time.perf_counter()
        gw = loaded_sweep.sweepheader.gatewidth
        rect = polar.polar2rect(gw, vectorized=False)
        t_stop = time.perf_counter()
        print("polar2rect generated in %.3f secs." % (t_stop-t_start))

        #generate rect image from rect object
        t_start = time.perf_counter()
        img_rect = generate_rect_image_from_rect(rect)
        t_stop = time.perf_counter()
        print("rect image from rect generated in %.3f secs." % (t_stop-t_start))

        #save rect image to disk
        t_start = time.perf_counter()
        img_rect_path = os.path.join(script_dir, os.path.basename(file_name) + ".rect.png")
        img_rect.save(img_rect_path)
        t_stop = time.perf_counter()
        print("rect image saved in %s in %.3f secs." % (img_rect_path, t_stop-t_start))

        #generate rect from polar using vectorized technique
        t_start = time.perf_counter()
        gw = loaded_sweep.sweepheader.gatewidth
        rect_vect = polar.polar2rect(gw, size=None, vectorized=True)
        t_stop = time.perf_counter()
        print("polar2rect vectorized generated in %.3f secs." % (t_stop-t_start))

         #generate rect image from rect_vect object
        t_start = time.perf_counter()
        img_rect_vect = generate_rect_image_from_rect(rect_vect)
        t_stop = time.perf_counter()
        print("rect_vect image from rect_vect generated in %.3f secs." % (t_stop-t_start))

        #save rect_vect image to disk
        t_start = time.perf_counter()
        img_rect_vect_path = os.path.join(script_dir, os.path.basename(file_name) + ".rect_vect.png")
        img_rect_vect.save(img_rect_vect_path)
        t_stop = time.perf_counter()
        print("rect_vect image saved in %s in %.3f secs." % (img_rect_vect_path, t_stop-t_start))

    return 0

if __name__ == '__main__':
    main()
