#!/usr/bin/env python

"""
This script will convert a percentile score layer to a decile raster layer based on the following values;

1 = 0-10%
2 = 10.001-20%
3 = 20.001-30%
4 = 30.001-40%
5 = 40.001-50%
6 = 50.001-60%
7 = 60.001-70%
8 = 70.001-80%
9 = 80.001-90%
10 = 90.001-100%


Author: Grant Staben
email: Grant.Staben@ntg.gov.au
Date:10/05/2022

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

inimage: str
             is a string containing the name of the input percentile score raster layer 
             
output : str 
            is the directory path and name of the output decile raster image following the naming convetion: NT_201805201904_decile_rainfall_a2.tif

"""

# import the modules
import sys
import os
import argparse
import pdb
import numpy as np 
from rios import applier, fileinfo
from osgeo import gdal


def getCmdargs():

    p = argparse.ArgumentParser()

    
    p.add_argument("-i","--inimage", help="input percentile score total rainfall image")
    
    p.add_argument("-o","--output", help="directroy path and name of the output image")
    
    cmdargs = p.parse_args()
    
    if cmdargs.inimage is None:

        p.print_help()

        sys.exit()

    return cmdargs


def mainRoutine():
    
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    
    infiles.perc = cmdargs.inimage
    outfiles.outfile = cmdargs.output
    
    controls = applier.ApplierControls()
    controls.setOutputDriverName('GTiff')
    options = ['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES', 'INTERLEAVE=BAND','BLOCKXSIZE=256','BLOCKYSIZE=256']
    controls.setCreationOptions(options)
    controls.setWindowXsize(256)
    controls.setWindowYsize(256)
    controls.setStatsIgnore(0)
    controls.setReferenceImage(infiles.perc)
    
    applier.apply(decile, infiles, outfiles, otherargs,controls=controls) 
    
    # set the no data value to 
    newImg = gdal.Open(cmdargs.output, gdal.GA_Update)
    newImg.GetRasterBand(1).SetNoDataValue(-1)

    
def decile(info, inputs, outputs, otherargs):
    
    """
    Function to convert percentile into decile ranks 
    """
    perc = np.array(inputs.perc[0])
    perc[perc == -32767.0] = -1
    perc[(perc <= 10.00000) & (perc >=0)] = 1
    perc[(perc > 10.00001) & (perc <= 20.0)] = 2
    perc[(perc > 20.00001) & (perc <= 30.0)] = 3
    perc[(perc > 30.00001) & (perc <= 40.0)] = 4
    perc[(perc > 40.00001) & (perc <= 50.0)] = 5
    perc[(perc > 50.00001) & (perc <= 60.0)] = 6
    perc[(perc > 60.00001) & (perc <= 70.0)] = 7
    perc[(perc > 70.00001) & (perc <= 80.0)] = 8
    perc[(perc > 80.00001) & (perc <= 90.0)] = 9
    perc[(perc > 90.00001) & (perc <= 100.0)] = 10
        
    output = np.array([perc], dtype=np.int16)
       
    outputs.outfile = output
    
if __name__ == "__main__":
    mainRoutine()