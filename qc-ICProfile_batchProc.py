#############################START LICENSE##########################################
# Copyright (C) 2019 Pedro Martinez
#
# # This program is free software: you can redistribute it and/or modify
# # it under the terms of the GNU Affero General Public License as published
# # by the Free Software Foundation, either version 3 of the License, or
# # (at your option) any later version (the "AGPL-3.0+").
#
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# # GNU Affero General Public License and the additional terms for more
# # details.
#
# # You should have received a copy of the GNU Affero General Public License
# # along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# # ADDITIONAL TERMS are also included as allowed by Section 7 of the GNU
# # Affero General Public License. These additional terms are Sections 1, 5,
# # 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apache-2.0")
# # where all references to the definition "License" are instead defined to
# # mean the AGPL-3.0+.
#
# # You should have received a copy of the Apache-2.0 along with this
# # program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
#############################END LICENSE##########################################


###########################################################################################
#
#   Script name: qc-ICProfile
#
#   Description: Tool for batch processing and report generation of ICProfile files
#
#   Example usage: python qc-ICProfile "/folder/"
#
#   Author: Pedro Martinez
#   pedro.enrique.83@gmail.com
#   5877000722
#   Date:2019-04-09
#
###########################################################################################



import os
import sys
import pydicom
import re
import argparse
import linecache
import tokenize
from PIL import *
import subprocess
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
import numpy as np
import pandas as pd
from openpyxl import Workbook, cell, load_workbook
from math import *
import scipy.integrate as integrate




def area_calc(profile,coord):
    # print(profile,coord)
    area = np.trapz(profile,coord)
    return area



def int_detc_indx(CorrCounts,FRGN):
    max_l = np.amax(CorrCounts[0:len(CorrCounts) // 2])
    max_r = np.amax(CorrCounts[len(CorrCounts) // 2:len(CorrCounts)])
    for i in range(0, len(CorrCounts) // 2):  # for the left side of the array
        if CorrCounts[i] <= max_l / 2 and CorrCounts[i + 1] > max_l / 2:
            lh = i + (max_l / 2 - CorrCounts[i]) / (CorrCounts[i + 1] - CorrCounts[i])

    for j in range(len(CorrCounts) // 2, len(CorrCounts)-1):  # for the right side of the array
        if CorrCounts[j] > max_r / 2 and CorrCounts[j + 1] <= max_r / 2:
            rh = j + (CorrCounts[j] - max_r / 2) / (CorrCounts[j] - CorrCounts[j + 1])

    CM = (lh + rh) / 2


    lFRGN = CM + (lh - CM) * FRGN / 100
    rFRGN = CM + (rh - CM) * FRGN / 100
    print("lFRGN","rFRGN","lh","rh")
    print(lFRGN,rFRGN,lh,rh)

    lf = int(lFRGN)
    rf = int(rFRGN)

    return lf, rf, lFRGN, rFRGN, CM




def read_icp(dirname):
# this section reads the header and detects to what cells to write
    
#we need to read the calibration file that corresponds with     
    with os.scandir(dirname) as entries:
        Data_dict = {}
        key_list=[]
        key_list.append('X')
        key_list.append('Y')

        # These vectors will have the location of the sensors in the x, y and diagonal directions
        Y = (np.linspace(1,65,65)-33)/2
        X= np.delete(np.delete(Y,31),32)
        PD = np.delete(np.delete((np.linspace(1,65,65)-33)/2,31),32)
        ND=PD
        PDX = PD/ np.cos(pi / 4)
        PDY = PD/ np.sin(pi / 4)
        NDX = ND/ np.cos(pi / 4 - pi / 2)
        NDY = ND/ np.sin(pi / 4 - pi / 2)

        Data_dict['X']=np.pad(X,(0,2),'constant',constant_values=0)
        Data_dict['Y']=Y
         #PD and ND also use the same number of detectors
        for filename in entries:
            if filename.is_file():
                if os.path.splitext(filename.name)[1]=='.prs':
                    print('Start header processing')
                    file = open(filename, mode='r', encoding='ISO-8859-1') #,encoding='utf-8-sig')
                    lines = file.readlines()
                    file.close()
                    calname = 'N:'+lines[5].rstrip().split('N:')[1]
                    # gain = int(re.findall(r'\d+',lines[20])[0])  # using regex
                    gain = int(lines[20].rstrip().split('\t')[1])
                    print(lines[29].split('\t'))
                    mode = lines[29].rstrip().split('\t')[1]
                    energy = lines[29].rstrip().split('\t')[3]
                    print('Calibration file name = ',calname)
                    print('Gain = ',gain)
                    print('Mode = ',mode)
                    print('Energy = ',energy)
                    my_dict = {}
                    my_list = []
                    if mode=='X-Ray FFF' and gain!=2:
                        print('Error, gain was set incorrectly')
                        exit(0)
                    print('Start data processing')
                    # reading measurement file
                    df = pd.read_csv(filename,skiprows=106,delimiter='\t')
                    tblen = df.shape[0]  #length of the table
                    #These vectors will hold the inline and crossline data
                    RawCountXvect = []
                    CorrCountXvect=[] # correcting for leakage using the expression # for Detector(n) = {RawCount(n) - TimeTic * LeakRate(n)} * cf(n)
                    RawCountYvect = []
                    CorrCountYvect=[]
                    RawCountPDvect = [] # positive diagonal
                    CorrCountPDvect=[]
                    RawCountNDvect = [] # negative diagonal
                    CorrCountNDvect=[]
                    BiasX=[]
                    CalibX=[]
                    BiasY=[]
                    CalibY=[]
                    BiasPD=[]
                    CalibPD=[]
                    BiasND=[]
                    CalibND=[]
                    Timetic=df['TIMETIC'][3]

                    QuadWedgeCal=[0.5096,0,0,0,0,0,0,0,0] # 6xqw,15xqw,6fffqw,10fffqw,6eqw,9eqw,12eqw,16eqw,20eqw
                    # figs = [] #in this list we will hold all the figures
                    print('Timetic=',Timetic*1e-6,df['TIMETIC']) # duration of the measurement
                    # print('Backrate',df)
                    for column in df.columns[5:68]: #this section records the X axis (-)
                        CorrCountXvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)#the corrected data for leakage = Timetic*Bias*Calibration/Gain
                        BiasX.append(df[column][0]) # already used in the formula above but saving them just in case
                        CalibX.append(df[column][1])
                        RawCountXvect.append(df[column][3])
                    for column in df.columns[68:133]: #this section records the Y axis (|)
                        CorrCountYvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
                        BiasY.append(df[column][0]) # already used in the formula above but saving them just in case
                        CalibY.append(df[column][1])
                        RawCountYvect.append(df[column][3])
                    for column in df.columns[133:196]: #this section records the D1 axis  (/)
                        CorrCountPDvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
                        BiasPD.append(df[column][0]) # already used in the formula above but saving them just in case
                        CalibPD.append(df[column][1])
                        RawCountPDvect.append(df[column][3])
                    for column in df.columns[196:259]: #this section records the D2 axis  (\)
                        CorrCountNDvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
                        BiasND.append(df[column][0]) # already used in the formula above but saving them just in case
                        CalibND.append(df[column][1])
                        RawCountNDvect.append(df[column][3])
                    # wb = Workbook()
                    # ws = wb.active
                    # ws.append()
                    # wb.save(dirname+"output.xlsx")
                    print(os.path.splitext(filename.name)[0])
                    key_list.append(os.path.splitext(filename.name)[0]+'_X')
                    key_list.append(os.path.splitext(filename.name)[0]+'_Y')
                    key_list.append(os.path.splitext(filename.name)[0]+'_PD')
                    key_list.append(os.path.splitext(filename.name)[0]+'_ND')

                    #we need to pad these arrays
                    CorrCountXvect.extend([0,0])
                    CorrCountPDvect.extend([0,0])
                    CorrCountNDvect.extend([0,0])

                    Data_dict[os.path.splitext(filename.name)[0]+'_X']=CorrCountXvect
                    Data_dict[os.path.splitext(filename.name)[0]+'_Y']=CorrCountYvect
                    Data_dict[os.path.splitext(filename.name)[0]+'_PD']=CorrCountPDvect
                    Data_dict[os.path.splitext(filename.name)[0]+'_ND']=CorrCountNDvect
                    

        print(Data_dict)
        df = pd.DataFrame(Data_dict,columns=key_list)
        print(df.describe)
        df.to_excel(dirname+'curves.xlsx',sheet_name='Sheet1')
        exit(0)







if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # pylint: disable = invalid-name
    parser.add_argument( "folder", help="path to file")
    args = parser.parse_args()  # pylint: disable = invalid-name

    if args.folder:
        dirname = args.folder  # pylint: disable = invalid-name
        read_icp(dirname)












