#!/usr/bin/env python
"""
This script finds all the files based on the end of the file name in a given folder and sub folders
and returns a list showing the path and file name. 


Created on Wed Jan 13 10:41:41 2016

Grant Staben

Modified: 15/11/2021

###############################################################################################

MIT License

Copyright (c) 2021 Grant Staben

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

direc : str 
            is a directory path to the location of the directory and sub-directories to search.

endfilen : str
            is a string indetifying the end of the file name to search for e.g. rain.tif .

yearM_f : str
            is a string containing the year and month (e.g. 202112)the defining the end of the seasonal period for the total rainfall grid.

txtfile : str 
            is a string with the directory and the output txt or csv file name containing the list of files.

"""


import fnmatch
import os
import argparse
import sys
import csv
import fnmatch

def getCmdargs():
    """
    Command line arguments to indentify the directory and the file extentin to create a list for
    """
    p = argparse.ArgumentParser()

    p.add_argument("-d","--direc", help="path to directory to look in")
    
    p.add_argument("-e","--endfilen", help="end of the file name e.g. h99m2.img")

    p.add_argument("-o","--txtfile", help="name of out put txt or csv file containing the list of files")
    
    
    cmdargs = p.parse_args()
    
    if cmdargs.direc is None:

        p.print_help()

        sys.exit()

    return cmdargs


def listdir(dirname,endfilename):
    """
    this function will return a list of files in a directory for the given file extention. 
    """
    list_img = []
    
    
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if (os.path.join(root, file)):
                img = (os.path.join(root, file))
                list_img.append(img)
                    
    return list_img

   
def mainRoutine():
    
    """
    main routine
    """
    
    cmdargs = getCmdargs() # instantiate the get command line function
    
    direc = cmdargs.direc 
    endfilename = cmdargs.endfilen
    
    txtname = cmdargs.txtfile
     
    list_img = listdir(direc,endfilename)
        
    # assumes that filelist is a flat list, it adds a  
    with open(txtname, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for file in list_img:
            writer.writerow([file])

if __name__ == "__main__":
    mainRoutine()
