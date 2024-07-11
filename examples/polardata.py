#!/bin/env python

#import from system
import sys
import os
import math
import argparse
from PIL import Image, ImageDraw

#safe pymetranet import
import import_pymetranet
from pymetranet import PolarSweepSerializer, PolarPpiData

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
        
        #generate waterfall image
        img_waterfall = Image.new("RGB", (polar.num_gates, polar.num_rays), (255, 255, 255))
        for i in range(polar.num_rays):
            for j in range(polar.num_gates):
                if not math.isnan(polar.data[i][j]):
                    img_waterfall.putpixel((j, i), (0, 0, 0))
        
        #save waterfall image to disk
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        img_waterfall_path = os.path.join(script_dir, os.path.basename(file_name) + ".waterfall.png")
        img_waterfall.save(img_waterfall_path)
        print("image saved in %s" % img_waterfall_path)
        
        #generate polar image
        radar_height = loaded_sweep.sweepheader.radarheight
        gate_width = loaded_sweep.sweepheader.gatewidth
        middle_ray_idx = int(len(loaded_sweep.rays) / 2)
        elevation = loaded_sweep.rays[middle_ray_idx].get_startel_deg() #elevation of central ray
        sin_elev = math.sin(math.radians(elevation))
        cos_elev = math.cos(math.radians(elevation))
        num_gates = polar.num_gates
        not_use_earth_curvature = False
        img_polar = Image.new("RGB", (polar.num_gates, polar.num_gates), (255, 255, 255))
        for i in range(polar.num_rays):
            for j in range(polar.num_gates):
                #if data is NODATA skip it and do not draw it
                if math.isnan(polar.data[i][j]):
                    continue
                    
                #calculate current gate range
                if not_use_earth_curvature:
                    cur_range = (j * gate_width)
                else:
                    #adjust range taking into account the elevation of the sweep and the earth curvature
                    gate_range = (j + 0.5) * gate_width
                    gate_height, gate_horizon_distance = calc_range(gate_range, sin_elev, cos_elev, radar_height)
                    cur_range = gate_horizon_distance
                
                #calculation of x, y, with original az
                orig_az_x = cur_range * math.sin(math.radians(i))
                orig_az_y = cur_range * math.cos(math.radians(i))
                
                x_pixel = round(orig_az_x / gate_width)
                y_pixel = round(orig_az_y / gate_width)
                x_pixel = round((num_gates / 2) + x_pixel)
                y_pixel = round((num_gates / 2) - y_pixel)
                if x_pixel < 0 or x_pixel >= num_gates:
                    #print("x_pixel exceeds width of image which is %d" % num_gates)
                    pass
                elif y_pixel < 0 or y_pixel >= num_gates:
                    #print("y_pixel exceeds height of image which is %d" % num_gates)
                    pass
                else:
                    img_polar.putpixel((x_pixel, y_pixel), (0, 0, 0))
        
        #save polar image to disk
        img_polar_path = os.path.join(script_dir, os.path.basename(file_name) + ".polar.png")
        img_polar.save(img_polar_path)
        print("image saved in %s" % img_polar_path)

    return 0

if __name__ == '__main__':
    main()
