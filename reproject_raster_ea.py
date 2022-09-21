#!/usr/bin/env python

"""
Script to reproject total monthly rainfall raster imagery to GDA94 / Australian Albers. 

Grant Staben
28/04/2022

###############################################################################################

MIT License

Copyright (c) 2022 Grant Staben

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

###############################################################################################

Parameters: 
-----------

img : str 
            is a directory path and name of the raster image to reproject to GDA94 / Australian Albers.

"""


import sys
import os
import argparse
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import pdb


#function to get cmd line inputs
def getCmdargs():
    
    p = argparse.ArgumentParser()
    
    p.add_argument("-i","--img", help="raster imagery to reproject to GDA94 / Australian Albers")
 

    cmdargs = p.parse_args()
    
    if cmdargs.img is None:

        p.print_help()

        sys.exit()

    return cmdargs

   
def main():
    
    cmdargs = getCmdargs()
        
    # open the list of imagery and read it into memory
    inImage = cmdargs.img
        
    # create the output file name by removeing the .shp and replacing it with .tif
    out_img = inImage[:-4] + "_a2.tif"
    print (out_img)
              
    #pdb.set_trace()
        
    dst_crs = 'EPSG:3577'

    with rasterio.open(inImage) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs,'transform': transform,'width': width,'height': height})
                        
        with rasterio.open(out_img, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source=rasterio.band(src, i),destination=rasterio.band(dst,i),src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs=dst_crs,resampling=Resampling.nearest)
    print (out_img, ' has been reprojected')
    
    repro_img = out_img
    
    src.close()

if __name__ == "__main__":
    main()