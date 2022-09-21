#!/usr/bin/env python

"""
Script to clip raster image to the NT boundary projected in GDA94 / Australian Albers 

Grant Staben
03/05/2022

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

img      : str 
            is a directory path and name of the raster image to reproject to GDA94 / Australian Albers.


outputNT : str 
            is a string with the directory and the output raster file name.


"""


import sys
import os
import argparse
import gdal
import pandas as pd
import fiona
import rasterio
import rasterio.mask
import pdb


def getCmdargs():
    
    #function to get cmd line inputs
    
    p = argparse.ArgumentParser()
    
    p.add_argument("-i","--img", help="raster imagery and the corresponding shapefiles used to clip the raster")
    
    p.add_argument("-o","--outputNT", help="path name of raster file for the clipped imagery")
       
    cmdargs = p.parse_args()
    
    if cmdargs.img is None:

        p.print_help()

        sys.exit()

    return cmdargs

   
def main():
    
    """
    main routine 
    """
    
    cmdargs = getCmdargs()
        
    # open the list of imagery and read it into memory
    inImage = cmdargs.img
    
    # location of the nt boundary projected in GDA94 / Australian Albers 
    inshp = "E:/DEPWS/code/rangeland_monitoring/PLB_report/nt_bnd/nt_bnd_ea.shp"
    out_tif = cmdargs.outputNT  
    print (out_tif)
        
    # read in the shapefile used to clip the raster image
    with fiona.open(inshp, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
        
    # read in the raster image to be clipped
    with rasterio.open(inImage) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
            
    out_meta.update({"driver": "GTiff","height": out_image.shape[1],"width": out_image.shape[2],"transform": out_transform})
        
    with rasterio.open(out_tif, "w",**out_meta) as dest:
        dest.write(out_image)
          
    src.close()

if __name__ == "__main__":
    main()