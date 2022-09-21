#!/usr/bin/env python

"""
This code runs a number of scripts to caluculate the total rainfall for a seasonal period defined by the user. The script generates
a list of all available monthly rainfall .tif files located in the coporate drive (Z:\Landsat\rainfall\) and then selects 
out the requried preiod based on the year and month defined by the user. 

The script also reprojects the output grid to GDA94 / Australian Albers and clips out the total rainfall grid out the the NT boundary.

The Monthly rainfall grids used are produced by the QLD goverment https://www.longpaddock.qld.gov.au/silo/gridded-data/  


Author: Grant Staben
email: grant.staben@nt.gov.au
Date: 26/04/2022
Version: 1.0

###############################################################################################

MIT License

Copyright (c) 2020 Grant Staben

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

txtfile : str 
            is a string to name of the txt file or csv file containing the list of monthly rainfall grids used to produce the output 
            total rainfall grid.

yearM_S : str
            is a string containing the year and month (e.g. 202101) the defining the start of the seasonal period for the 
            total rainfall grid.

yearM_f : str
            is a string containing the year and month (e.g. 202112)the defining the end of the seasonal period for the total rainfall grid.

output : str 
            is a string with the directory and the output file name given to the total rainfall seasonal grid.

"""


# import the requried modules
import sys
import os
import argparse
import pandas as pd
import fnmatch
import csv


#function to get cmd line inputs
def getCmdargs():
    
    p = argparse.ArgumentParser()
    
    p.add_argument("-o","--txtfile", help="name of out put txt file containing the list of files used to calculate the total rainfall")
    
    p.add_argument("-s", "--yearM_S", help="the year and month identifying the start of the seasonal period i.e. 202010")
    
    p.add_argument("-f", "--yearM_f", help="the year and month identifying the end of the seasonal period i.e. 202104")
    
    p.add_argument("-a","--output", help="provide the output directory and file name for the total rainfall grid")
    
    p.add_argument("-n","--outputNT", help="provide the output directory and file name for the NT total rainfall grid")
    
    cmdargs = p.parse_args()
    if cmdargs.yearM_S is None:
        p.print_help()
        sys.exit()

    return cmdargs
    
def create_rainfall_list(dirname,endfilename,txtname): 
    
    """
    create the list of available rainfall grids
    
    """
    cmd = "python list_of_files_multi_dir.py --direc %s --endfilen %s --txtfile %s"% (dirname,endfilename, txtname) 
       
    os.system(cmd)
    
    
    
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
       

def main():
    """
    Main routine
    """
    
    cmdargs = getCmdargs()
   
    # cmdargs for the image list script 
    dirname = "Z:/Landsat/rainfall/" 
    endfilename = "rain.tif"
    txtname = cmdargs.txtfile
    nt_clip = cmdargs.outputNT
    
    # cmdargs for the output seasonal rainfall grid 
    newf = cmdargs.output
    
    create_rainfall_list(dirname,endfilename,txtname)
   
    # select the date range for the seasonal total rainfall grid 
    df=pd.read_csv(txtname,header=None)
    
    # extract out the year and month from the individual monthly rainfall grids
    df['yearM'] = df[0].map(lambda x: str(x)[-23:-17]).astype(int)
    
    # do the selection for the period to calculate   
    yearM_start = int(cmdargs.yearM_S)
    yearM_finish = int(cmdargs.yearM_f)
                  
    imglist = df[(df['yearM'] >= yearM_start) & (df['yearM'] <= yearM_finish)]
    img_to_process=imglist[0]
     
    # write out the list of rainfall grids to obtain the total
    with open(txtname, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for file in img_to_process:
            writer.writerow([file])
            
    # call the total rainfall script
    total_rainfall(txtname, newf)
    
    # call the reporject script 
    repro(newf)
    
    # clip the reprojected rainfall grid to the NT boundary
    img = newf[:-4] + "_a2.tif"
    
    out_nt = nt_clip
           
    clipNT(img,out_nt)
    
    
if __name__ == "__main__":
    main()    