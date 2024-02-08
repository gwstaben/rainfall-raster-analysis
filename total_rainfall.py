#!/usr/bin/env python

""" this script produces a total rainfall grid using the SILO monthly rainfall grids for any given period""" 



from __future__ import print_function, division
import sys
from rios import applier, fileinfo
import numpy as np
import csv
import pdb
from osgeo import gdal
import argparse
import pandas as pd
import scipy.stats.mstats as mstats
import numpy.ma as ma


def getCmdargs():
    """
    Get command line arguments
    """
    p = argparse.ArgumentParser()
    p.add_argument("--imglist", help="Input list of imagery to calculate the total rainfall for the given period")
    p.add_argument("--output", help="provide the output directory and file name")
    
    cmdargs = p.parse_args()
    
    if cmdargs.imglist is None:
        p.print_help()
        sys.exit()
        
    return cmdargs

def readlist(imglist):

    """
    This block of code reads in a csv file containing 
    a list of lists and converts them to a flat list to imput into rios
    """
    
    df = pd.read_csv(imglist,header=None)
       
    flat_list = df[0].tolist()

    return flat_list


def dostats(info, inputs, outputs, otherargs):
    
    """
    Called from RIOS. calculate the sum of all the monthly rainfall for each year             
    """
    np.seterr(all='ignore')
    
    nullValue  = otherargs.coverNull
    # select the first band in the image.
    index = 0
    # read in the list of images for the given year and iterate over each pixel masking out the nodata values.
    changeImg = np.array([img[0] for img in inputs.images])
    maskechangeImg = ma.masked_array(changeImg,changeImg==0)   
  
    Total_rainfall = np.ma.sum(maskechangeImg, axis=0) # calucate the total rainfall for a given period output in mm 
    # set the nodata value to -1
    Total_rainfall[Total_rainfall < 0] = -1 
    # output the total rainfall as a interger value
    outputs.stats=np.array([Total_rainfall],dtype=np.int)     


def mainRoutine():

    """Run mainRoutine"""

    cmdargs = getCmdargs()
    
    imglist = cmdargs.imglist           
    # create the output file name for the given year    
    newf = cmdargs.output
               
    # create the list of  rainfall grids to calculate the total rainfall   
    flat_list = readlist(imglist)
    print (flat_list)
    #Set up rios to apply images
    controls = applier.ApplierControls()
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    
    # read in the list of imagery to calculate the mean
    infiles.images = flat_list 
    otherargs = applier.OtherInputs()
    imginfo = fileinfo.ImageInfo(infiles.images[0])
    # set up the nodata values
    otherargs.coverNull = imginfo.nodataval[0]
    print (otherargs.coverNull)
    controls.setStatsIgnore(otherargs.coverNull)
        
    outfiles.stats = newf
    
    applier.apply(dostats, infiles, outfiles, otherargs, controls=controls)
        
    print (newf + ' is complete')
    
    """set the new no data value so 
    when it is open in arcmap or qgis it recognises the new values"""
    
    newImg = gdal.Open(newf, gdal.GA_Update)
    newImg.GetRasterBand(1).SetNoDataValue(-1)
    
if __name__ == "__main__":
    mainRoutine()
