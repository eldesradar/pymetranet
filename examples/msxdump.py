#!/bin/env python

import sys
import argparse

#safe pymetranet import
import import_pymetranet
from pymetranet.volumesweep import PolarSweep, MomentInfo
from pymetranet.volumesweep_serializer import PolarSweepSerializer

K_CONV_DEG = 360.0 / 65535.0

def get_az_deg(value):
    return (value & 0x0000FFFF) * K_CONV_DEG
        
def get_el_deg(value):
    return 0 if (value >> 16) == 0xFFFF else (value >> 16) * K_CONV_DEG
        
def get_moment_info(sweep_header, moment_name):
    for mom_info in sweep_header.momentsinfo:
        if mom_info.name == moment_name:
            return mom_info
            
    return None

def get_moment(sweep, ray, mom_info):
    for mom in ray.moments:
        if mom.datamomentheader.momentid == mom_info.momentid:
            return mom
            
    return None

def dump_sweep_header(sweep_header, args=None):
    print("header.FileId: '%s'" % sweep_header.fileid)
    print("header.Version: %d" % sweep_header.version)
    print("header.Length: %d" % sweep_header.length)
    print("header.RadarName: '%s'" % sweep_header.radarname)
    print("header.ScanName: '%s'" % sweep_header.scanname)
    print("header.RadarLat: %g" % sweep_header.radarlat)
    print("header.RadarLon: %g" % sweep_header.radarlon)
    print("header.RadarHeight: %g" % sweep_header.radarheight)
    print("header.SequenceSweep: %d" % sweep_header.sequencesweep)
    print("header.CurrentSweep: %d" % sweep_header.currentsweep)
    print("header.TotalSweep: %d" % sweep_header.totalsweep)
    print("header.AntMode: %d" % sweep_header.antmode)
    print("header.Priority: %d" % sweep_header.priority)
    print("header.Quality: %d" % sweep_header.quality)
    print("header.RepeatTime: %d" % sweep_header.repeattime)
    print("header.NumMoments: %d" % sweep_header.nummoments)
    print("header.GateWidth: %g" % sweep_header.gatewidth)
    print("header.WaveLength: %g" % sweep_header.wavelength)
    print("header.PulseWidth: %g" % sweep_header.pulsewidth)
    print("header.StartRange: %g" % sweep_header.startrange)
    print("header.MetaDataSize: %d" % sweep_header.metadatasize)
    print("header.MetaData: '%s'" % sweep_header.metadata)
    
    #print moment info structures
    for i in range(sweep_header.nummoments):
        print("moment %d/%d Id: %d (%#X)" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].momentid, sweep_header.momentsinfo[i].momentid))
        print("moment %d/%d DataFormat: %d" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].dataformat))
        print("moment %d/%d NumBytes: %d" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].numbytes))
        print("moment %d/%d Normalized: %s" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].normalized))
        print("moment %d/%d Name: '%s'" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].name))
        print("moment %d/%d Unit: '%s'" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].unit))
        print("moment %d/%d FactorA: %g" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].factora))
        print("moment %d/%d FactorB: %g" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].factorb))
        print("moment %d/%d FactorC: %g" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].factorc))
        print("moment %d/%d ScaleType: %d" % (i+1, sweep_header.nummoments,
            sweep_header.momentsinfo[i].scaletype))
    
def dump_ray_header(ray, i, num_rays, args=None):
    azStart  = get_az_deg(ray.rayheader.startangle)
    azStop  = get_az_deg(ray.rayheader.endangle)
    eleStart = get_el_deg(ray.rayheader.startangle)
    eleStop = get_el_deg(ray.rayheader.endangle)
    
    if eleStart > 180:
        eleStart -= 360
    if eleStop > 180:
        eleStop -= 360
        
    #print header
    print("ray[%03d/%03d]:" % (i+1, num_rays))
    print("ray header.Length: %d" % ray.rayheader.length)
    print("ray header.StartAngle: %d Azimuth: %g deg Elevation: %g deg" %
        (ray.rayheader.startangle, azStart, eleStart))
    print("ray header.EndAngle: %d Azimuth: %g deg Elevation: %g deg" %
        (ray.rayheader.endangle, azStop, eleStop))
    print("ray header.Sequence: %d" % ray.rayheader.sequence)
    print("ray header.NumPulses: %d" % ray.rayheader.numpulses)
    print("ray header.DataBytes: %d" % ray.rayheader.databytes)
    print("ray header.Prf: %g" % ray.rayheader.prf)
    print("ray header.DateTime: %ld" % ray.rayheader.datetime)
    print("ray header.DataFlags: %d" % ray.rayheader.dataflags)
    print("ray header.MetaDataSize: %d" % ray.rayheader.metadatasize)
    print("ray header.NumBatches: %d" % ray.rayheader.numbatches)
    
    num_batches = len(ray.rayheader.batchesinfo)
    for i in range(num_batches):
        batch_info = ray.rayheader.batchesinfo[i]
        
        print("ray batch[%d/%d] Length: %d" % (i+1, num_batches,
            batch_info.length))
        print("ray batch[%d/%d] StartRange: %g" % (i+1, num_batches,
            batch_info.startrange))
        print("ray batch[%d/%d] Prf: %g" % (i+1, num_batches,
            batch_info.prf))
        print("ray batch[%d/%d] NumPulses: %d" % (i+1, num_batches,
            batch_info.numpulses))
        print("ray batch[%d/%d] Dprf: %d" % (i+1, num_batches,
            batch_info.dprf))
        print("ray batch[%d/%d] AngPerc: %g" % (i+1, num_batches,
            batch_info.angperc))
            
    print("ray header.MetaData: '%s'" % ray.rayheader.metadata)
    
    num_moments = len(ray.moments)
    for i in range(num_moments):
        mom = ray.moments[i]
        
        print("ray moment[%d/%d] MomentId: %d" % (i+1, num_moments,
            mom.datamomentheader.momentid))
        print("ray moment[%d/%d] DataSize: %d" % (i+1, num_moments,
            mom.datamomentheader.datasize))
    
def dump_mom_gates(mom, data_format, args=None):
    if data_format == MomentInfo.DATA_FORMAT_FIXED_8_BIT:
        fmt = "%03d "
    elif data_format == MomentInfo.DATA_FORMAT_FIXED_16_BIT:
        fmt = "%05d "
    elif data_format == MomentInfo.DATA_FORMAT_FLOAT_32_BIT:
        fmt = "%10g "
    else:
        raise Exception("Error reading moment gates: unrecognized data format")
        
    num_gates = len(mom.gates)
    s = ""
    for i in range(num_gates):
        if i % 10 == 0:
            s += "[%04d-%04d]: " % (i, i+9)
        if mom.gates[i] == 0:
            if data_format == MomentInfo.DATA_FORMAT_FIXED_8_BIT:
                s += "--- "
            elif data_format == MomentInfo.DATA_FORMAT_FIXED_16_BIT:
                s += "----- "
            elif data_format == MomentInfo.DATA_FORMAT_FLOAT_32_BIT:
                s += "    ------ "
        else:
            s += fmt % mom.gates[i]
        if (i+1) % 10 == 0:
            print(s)
            s = ""
            
def dump(sweep, args=None):
    dump_sweep_header(sweep.sweepheader, args)
    
    mom_info = None
    if args.mom:
        mom_info = get_moment_info(sweep.sweepheader, args.mom)
    
    num_rays = len(sweep.rays)
    for i in range(num_rays):
        ray = sweep.rays[i]
        
        if args.ray != -1:
            if i+1 == args.ray:
                #print("args.mom is not empty ('%s') and i+1 (%d) is equal to args.ray (%d)" % (args.mom, i+1, args.ray))
                dump_ray_header(ray, i, num_rays, args)
                if mom_info is not None:
                    mom = get_moment(sweep, ray, mom_info)
                    print("%d gates of %s (format: %d) for ray %d:" %
                        (len(mom.gates), args.mom, mom_info.dataformat, i+1))
                    dump_mom_gates(mom, mom_info.dataformat, args)
        elif args.ray_from != -1:
            if i+1 >= args.ray_from and i+1 <= args.ray_to:
                #print("args.mom is not empty ('%s') and i+1 (%d) is equal to args.ray (%d)" % (args.mom, i+1, args.ray))
                dump_ray_header(ray, i, num_rays, args)
                if mom_info is not None:
                    mom = get_moment(sweep, ray, mom_info)
                    print("%d gates of %s (format: %d) for ray %d:" %
                        (len(mom.gates), args.mom, mom_info.dataformat, i+1))
                    dump_mom_gates(mom, mom_info.dataformat, args)
        else:
            #print("args.ray is -1 (%s) or args.ray_from is -1 (%d) dump header of ray %d" % (args.ray, args.ray_from, i+1))
            dump_ray_header(ray, i, num_rays, args)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ray", type=int, default=-1)
    parser.add_argument("--ray-from", type=int, default=-1)
    parser.add_argument("--ray-to", type=int, default=-1)
    parser.add_argument("--mom", type=str, default="")
    #parser.add_argument("--show-dn", action="store_true")
    parser.add_argument('infile', nargs='*', type=str)
    
    args = parser.parse_args()
    #print(args)
    #print("args.infile: " + str(args.infile))
    #for i in range(len(args.infile)):
        #print("args.infile[%d]: '%s'" % (i, args.infile[i]))
    #return 0
    if args.ray != -1:
        if args.ray < 1:
            print("Argument error! You must specify a valid ray number (starting from 1) after the '--ray' flag")
            return 1
        args.ray_from = -1
        args.ray_to = -1
    if args.ray_from != -1:
        if args.ray_to == -1:
            args.ray_to = args.ray_from
        if args.ray_from < 1:
            print("Argument error! You must specify a valid ray number (starting from 1) after the '--ray-from' flag")
            return 1
     
    for file_name in args.infile:
        print("loading file %s..." % file_name)
        loaded_sweep = PolarSweepSerializer.load(file_name)
        print("file %s successfully loaded!" % file_name)
        dump(loaded_sweep, args)
    
    return 0

if __name__ == '__main__':
    main()
