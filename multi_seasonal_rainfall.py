#!/usr/bin/env python

"""
This code runs a number of scripts to calculate the total rainfall for a seasonal period. The script uses monthly rainfall .tif files located in the corporate drive (Z:\Landsat\rainfall\).

It will loop produce a seasonal total rainfall grid for every period based on the raster data available.

The script also reprojects the output grid to GDA94 / Australian Albers and clips out the total rainfall grid out the NT boundary.

The Monthly rainfall grids used are produced by the QLD government https://www.longpaddock.qld.gov.au/silo/gridded-data/

Author: Grant Staben
email: grant.staben@nt.gov.au
Date: 03/06/2022
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
            is a string to name of the txt file or csv file containing the list of monthly rainfall grids used to produce the output 
            total rainfall grid.

sameYear: str
             is a string [y or n] that identifies if the seasonal period is calculated from the same year or covers two years e.g. 2021 to 2022
             
smonth: str
            is a string that identifies the month to start the seasonal period.
            
fmonth: str
            is a string that identifies the month to finsih the seasonal period.

output : str 
            is a string with the directory for the AU total rainfall seasonal grid.
            
outputNT : str 
            is a string with the directory for the NT total rainfall seasonal grid.

"""


import os
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
    p.add_argument("-i","--imglist", help="Input list of imagery to calculate the total rainfall for the given period")
    p.add_argument("-y","--sameYear", help="identifies if the seasonal period starts and finishs in the same year or covers two different years e.g 2021 to 2022,  y = the same year, n = over two differnt years")
    p.add_argument("-s","--smonth", help="provide the start month e.g 05")
    p.add_argument("-f","--fmonth", help="provide the finish month e.g 05")
    p.add_argument("-o","--outdir", help="provide the output directory for the AU total rainfall grid")
    p.add_argument("-n","--outputNT", help="provide the output directory for the NT total rainfall grid")
    cmdargs = p.parse_args()
    
    if cmdargs.imglist is None:
        p.print_help()
        sys.exit()
        
    return cmdargs


    
def total_rainfall(txtname, newf):
    
    """
    call the total rainfall script and run it.
    
    """ 
    cmd = "python total_rainfall.py --imglist %s --output %s"% (txtname, newf) 
       
    os.system(cmd)
     
    print (newf + ' is complete')
    
    
def repro(newf):
    
    """
    call the total reproject script and run it.
    
    """ 
    cmd = "python reproject_raster_ea.py --img %s"% (newf) 
       
    os.system(cmd)
        
    print (newf + ' has been reprojected')

    
def clipNT(img,out_nt):

    
    cmd = "python clip_raster_nt_bnd_ea.py --img %s --outputNT %s"% (img,out_nt)
    
    os.system(cmd)
    
    print (out_nt + ' has been clipped to the NT boundary')
    
    
    
    
def mainRoutine():

    """Run mainRoutine"""

    cmdargs = getCmdargs()
    
    imglist = cmdargs.imglist
    
    outdir = cmdargs.outdir 
    
    nt_outdir = cmdargs.outputNT
    
    same_year = cmdargs.sameYear
    
    
    print (nt_outdir)
    
    df = pd.read_csv(imglist,header=None)
    
    years = df[0].map(lambda x: str(x)[-23:-19]).unique()

    # create the datetime field from the monthly rainfall data to enable selection of the selected time period 
    df['img_date'] = pd.to_datetime((df[0].map(lambda x: str(x)[-23:-19]) + '-' + df[0].map(lambda x: str(x)[-19:-17]) + '-' + '01'),yearfirst=True, dayfirst=False)

    # start and finsih months 
    sm = cmdargs.smonth
    fm = cmdargs.fmonth

    for year in years:
    
        # create the ym start and finish period 
        ys = str(year) + '-' + sm + '-01'
        
        # calculates the year period to process this can be over the same year or over two consecitive years 2021 to 2022
        if same_year == 'y':            
            yf = str(year) + '-' + fm + '-01'
        else:
            yf = str(int(year)+1) + '-' + fm + '-01'
            
        # create the year + month start and finish time for the output file name
        ysm = str(year) + sm
                
        if same_year == 'y':            
            yfm = str(year) + fm
        else:            
            yfm = str(int(year)+1) + fm  
    
        print (ys, yf)
    
        df_select = df[(df['img_date'] >= ys) & (df['img_date'] <= yf)]
        
        listimg = df_select[0].values.tolist()
        
        print (listimg)
        print ('***************************')
    
    
        filename = outdir  + '\AU_'+ ysm + yfm + '_total_rainfall.tif'
        
               
        print (filename)
        print ("----------------------------------------------------------------------------------------------------")
    
        # write out the selected monthly rainfall grids to a tempory csv file  
        with open('temp_list.csv', "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            for file in listimg:
                writer.writerow([file])
        
        txtname = 'temp_list.csv'
        
        print ('***************************')
        newf  = outdir  + '\AU_' + ysm + yfm + '_total_rainfall.tif'
       
        total_rainfall(txtname, newf) 
        
        
        # call the reporject script 
        repro(newf)
    
        # clip the reprojected rainfall grid to the NT boundary
        img = newf[:-4] + '_a2.tif'
        
        out_nt = nt_outdir + "/NT_" + ysm + yfm + "_total_rainfall_a2.tif"
        
        print (out_nt)
           
        clipNT(img,out_nt)
    
if __name__ == "__main__":
    mainRoutine()