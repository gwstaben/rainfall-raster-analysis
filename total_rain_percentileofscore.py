#!/usr/bin/env python
"""
This script produces percentile score for total rainfall for a given period compared with the longterm values for the user defined 
number of years.


Author: Grant Staben
email: grant.staben@nt.gov.au
Date: 03/05/2022
Version: 1.0

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

imglist : str 
            is a string to name of the txt file or csv file containing the list of seasonal rainfall grids used to compare the current seasonal period with.

img: str
             is a string containing the name of the input file to calculate the percentile score 
             
output : str 
            is a name of the output percentile score image following the naming convetion: NT_201805201904_perc_rainfall_a2.tif.
            
"""

from __future__ import print_function, division
import sys
import os
from rios import applier, fileinfo
import numpy as np
import csv
import pdb
import argparse
import pandas as pd
from osgeo import gdal
import scipy.stats.mstats as mstats
import numpy.ma as ma
from scipy import stats


def getCmdargs():
    """
    Get command line arguments
    """
    p = argparse.ArgumentParser()
    
    p.add_argument("-l","--imglist", help="input list of imagery to process, should be a pandas df without a header")
    
    p.add_argument("-i","--img", help="input imagery to calculate the percentile score")
    
    p.add_argument("-o","--outfile", help="name of the output percentile score image")
   
    cmdargs = p.parse_args()
    
    if cmdargs.imglist is None:
        p.print_help()
        sys.exit()
        
    return cmdargs


def mainRoutine():
    
    cmdargs = getCmdargs()
    
    # read in the list of disturbance layers to sum
    df=pd.read_csv(cmdargs.imglist,header=None)
         
    listimg = df[0].values.tolist()
    print (listimg)
    
    # set up rios
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    
    # read in the list of imagery to calculate the sum
    infiles.imglist = listimg
    infiles.img = cmdargs.img
    outfiles.stat1 = "temp_pecentile_output_to_delete.img"
       
    controls = applier.ApplierControls()
    controls.setOutputDriverName('GTiff')
    options = ['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES', 'INTERLEAVE=BAND','BLOCKXSIZE=256','BLOCKYSIZE=256']
    controls.setCreationOptions(options)
    controls.setWindowXsize(256)
    controls.setWindowYsize(256)
    
    # set up the nodata values
    imginfo = fileinfo.ImageInfo(infiles.img)
    otherargs.coverNull = imginfo.nodataval[0]   
    
    applier.apply(dostats, infiles, outfiles, otherargs,controls=controls)  


def dostats(info, inputs, outputs, otherargs):
    
    """
    Called from RIOS. calculate the percentile score for the selected image compared prevous rainfall totals
    in the list             
    """
    np.seterr(all='ignore')
    
    nullValue  = otherargs.coverNull
    # select the first band in the image.
    index = 0
    # read in the list of images for the given year and iterate over each pixel masking out the nodata values.
    stack = np.array([img[index] for img in inputs.imglist])
    maskedstack = ma.masked_array(stack,stack==nullValue)
    
    # read in the image to caluclate the percetile score 
    img = inputs.img
    masked_score = ma.masked_array(img,img==nullValue)
    
    x = int(maskedstack.shape[2])
    y = int(maskedstack.shape[1])
    z = int(maskedstack.shape[0])

    # get the shape of the array for the image to caluclate the percetile score
    scores = inputs.img.shape
        
    # extract out each of the array shape values to use in reshaping the array 
    x1 = int(masked_score.shape[2])
    y1 = int(masked_score.shape[1])
    z1 = int(masked_score.shape[0])
    
    #print (x1, y1, z1)

    
    # list to save the percentile score 
    ndata = []
    
    # iterate over the elements in the array to calculate the percentile score for the given values 
    for i in range(y):
    
        a1 = maskedstack[:,i]
        #print (a1)
    
        a2 = masked_score[:,i]
        
        for p in range(x):
        
            a1_1 = a1[:,p]
     
            score = a2[:,p]
        
            stat = stats.percentileofscore(a1_1, score)
            
            # this deals with any result that is zero and is being output as null data when it should indicate a very low value
            if stat == 0:
                
                stat = 0.01
            else:
                stat = stat
                
            # append the results to a list before reshaping them to output as an image 
            ndata.append(stat)
   
    new_array = np.array([ndata])
    
    rshape = new_array.reshape([z1,y1,x1])
   
    percImage = rshape
   
    results = np.zeros(scores, dtype=np.float32)
    
    results = percImage
    
    output = np.array(results,dtype=np.float32)
       
    outputs.stat1 = output
    

def apply_new_nodata():
    """
    This function applies a new nodata value to the percentile output
    it uses the nodata areas defined by the input image.
    """
    cmdargs = getCmdargs()
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    
    # read input img that the percentile has been calculated 
    infiles.img = cmdargs.img 
    
    # this reads in the output from applying the model 
    infiles.model = 'temp_pecentile_output_to_delete.img'
    
    # set up the output file name
    final_output = cmdargs.outfile
    
    outfiles.model_nodata = final_output

    applier.apply(defineNoData, infiles, outfiles, otherargs)
    
    # set the nodata value using gdal
    setNodataValue(final_output)
    
    # removes the temp file
    os.remove("temp_pecentile_output_to_delete.img")
    # needed if script is run on a windows system
    os.remove("temp_pecentile_output_to_delete.img.aux.xml")    

    
def defineNoData(info, inputs, outputs, otherargs):
    
    """ this function reads in the modelled data an applies a nodata value '
    based on the nodata values in the imput img"""
    
    # read in the percentile image 
    model = np.array(inputs.model)
        
    # read in a total rainfall img 
    mask = np.array(inputs.img.astype(np.float32))
    
    # use the total rainfall image to define the nodata areas in the percentile image.
    model[(mask==-1)] = -1

    # save out the percentile image with the nodata areas masked
    model_nodata = model   
    outputs.model_nodata = model_nodata

    
def setNodataValue(final_output):
    
    """this function sets the new no data value so 
    when it is open in arcmap or qgis it recognises the new values"""
    
    newImg = gdal.Open(final_output, gdal.GA_Update)
    newImg.GetRasterBand(1).SetNoDataValue(-1)
    
if __name__ == "__main__":
    mainRoutine()
    apply_new_nodata()