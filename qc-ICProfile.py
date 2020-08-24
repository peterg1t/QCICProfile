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


def xls_cell_spec(mode, energy):

    CellChange = {}
    Attributes=[]

    # cell specification for 6MV
    if mode == 'X-Ray' and energy == '6 MV':
        energy = 6
        beamtype = 'X'
        CellChange['F43'] = 0  # "FlatnessY"
        CellChange['G43'] = 0  # "FlatnessX"
        CellChange['F44'] = 0  # "SymmetryY"
        CellChange['G44'] = 0  # "SymmetryX"
        CellChange['H45'] = 0  # "CentralReading"
        Attributes = ['FlatnessY', 'FlatnessX', 'SymmetryY', 'SymmetryX', 'Central Reading']

        # cell specification for 10MV
    elif mode == 'X-Ray' and energy == '10 MV':
        energy = 10
        beamtype = 'X'
        CellChange['F46'] = 0  # "FlatnessY"
        CellChange['G46'] = 0  # "FlatnessX"
        CellChange['F47'] = 0  # "SymmetryY"
        CellChange['G47'] = 0  # "SymmetryX"
        # CellChange['H49'] = 0  # "CentralReading"
        Attributes = ['FlatnessY', 'FlatnessX', 'SymmetryY', 'SymmetryX']

    # cell specification for 15MV
    elif mode == 'X-Ray' and energy == '15 MV':
        energy = 15
        beamtype = 'X'
        CellChange['F47'] = 0  # "FlatnessY"
        CellChange['G47'] = 0  # "FlatnessX"
        CellChange['F48'] = 0  # "SymmetryY"
        CellChange['G48'] = 0  # "SymmetryX"
        CellChange['H49'] = 0  # "CentralReading"
        Attributes = ['FlatnessY', 'FlatnessX', 'SymmetryY', 'SymmetryX', 'Central Reading']

    # cell specification for 6FFF
    elif mode == 'X-Ray FFF' and energy == '6 MV':
        energy = 6
        beamtype = 'FFF'
        CellChange['F52'] = 0  # "UnflatnessY"
        CellChange['G52'] = 0  # "UnflatnessX"
        CellChange['F53'] = 0  # "SymmetryY"
        CellChange['G53'] = 0  # "SymmetryX"
        CellChange['H54'] = 0  # "CentralReading"
        Attributes = ['UnflatnessY', 'UnflatnessX', 'SymmetryY', 'SymmetryX', 'Central Reading']

    # cell specification for 10FFF
    elif mode == 'X-Ray FFF' and energy == '10 MV':
        energy = 10
        beamtype = 'FFF'
        CellChange['F57'] = 0  # "UnflatnessY"
        CellChange['G57'] = 0  # "UnflatnessX"
        CellChange['F58'] = 0  # "SymmetryY"
        CellChange['G58'] = 0  # "SymmetryX"
        CellChange['H60'] = 0  # "CentralReading"
        Attributes = ['UnflatnessY', 'UnflatnessX', 'SymmetryY', 'SymmetryX', 'Central Reading']

    # cell specification for 6MeV
    elif mode == 'Electron' and energy == '6 MeV':
        energy = 6
        beamtype = 'MeV'
        CellChange['G81'] = 0  # "R50"
        # CellChange['G57'] = 0  # "UnflatnessX"
        # CellChange['F58'] = 0  # "SymmetryY"
        # CellChange['G58'] = 0  # "SymmetryX"
        CellChange['J89'] = 0  # "CentralReading"
        Attributes = ['R50', 'D0']

    # cell specification for 9MeV
    elif mode == 'Electron' and energy == '9 MeV':
        energy = 9
        beamtype = 'MeV'
        CellChange['G82'] = 0  # "R50"
        # CellChange['G57'] = 0  # "UnflatnessX"
        # CellChange['F58'] = 0  # "SymmetryY"
        # CellChange['G58'] = 0  # "SymmetryX"
        CellChange['J90'] = 0  # "CentralReading"
        Attributes = ['R50', 'D0']

    # cell specification for 12MeV
    elif mode == 'Electron' and energy == '12 MeV':
        energy = 12
        beamtype = 'MeV'
        CellChange['G83'] = 0  # "R50"
        # CellChange['G57'] = 0  # "UnflatnessX"
        # CellChange['F58'] = 0  # "SymmetryY"
        # CellChange['G58'] = 0  # "SymmetryX"
        CellChange['J91'] = 0  # "CentralReading"
        Attributes = ['R50', 'D0']

    # cell specification for 16MeV
    elif mode == 'Electron' and energy == '16 MeV':
        energy = 16
        beamtype = 'MeV'
        CellChange['G84'] = 0  # "R50"
        # CellChange['G57'] = 0  # "UnflatnessX"
        # CellChange['F58'] = 0  # "SymmetryY"
        # CellChange['G58'] = 0  # "SymmetryX"
        CellChange['J92'] = 0  # "CentralReading"
        Attributes = ['R50', 'D0']

    # cell specification for 20MeV
    elif mode == 'Electron' and energy == '20 MeV':
        energy = 20
        beamtype = 'MeV'
        CellChange['G85'] = 0  # "R50"
        # CellChange['G57'] = 0  # "UnflatnessX"
        # CellChange['F58'] = 0  # "SymmetryY"
        # CellChange['G58'] = 0  # "SymmetryX"
        CellChange['J93'] = 0  # "CentralReading"
        Attributes = ['R50', 'D0']

    return CellChange, Attributes




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
    print("lFRGN","rFRGN")
    print(lFRGN,rFRGN)

    # lf = int(round(lFRGN)) + 1
    # rf = int(round(rFRGN))
    lf = int(lFRGN) + 1
    rf = int(rFRGN)

    return lf, rf, lFRGN, rFRGN, CM




def read_icp(filename):
# this section reads the header and detects to what cells to write
    
#we need to read the calibration file that corresponds with     



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


    CellChange, Attributes = xls_cell_spec(mode, energy)



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
    # These vectors will have the location of the sensors in the x, y and diagonal directions
    X=[-16,-15.5,-15,-14.5,-14,-13.5,-13,-12.5,-12,-11.5,-11,-10.5,-10,-9.5,-9,-8.5,-8,-7.5,-7,-6.5,-6,-5.5,-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,0,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16]
    Y=[-16,-15.5,-15,-14.5,-14,-13.5,-13,-12.5,-12,-11.5,-11,-10.5,-10,-9.5,-9,-8.5,-8,-7.5,-7,-6.5,-6,-5.5,-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,15.5,16]
    PD=[-22.6,-21.9,-21.2,-20.5,-19.8,-19.1,-18.4,-17.7,-17,-16.3,-15.6,-14.8,-14.1,-13.4,-12.7,-12,-11.3,-10.6,-9.9,-9.2,-8.5,-7.8,-7.1,-6.4,-5.7,-4.9,-4.2,-3.5,-2.8,-2.1,-1.4,0,1.4,2.1,2.8,3.5,4.2,4.9,5.7,6.4,7.1,7.8,8.5,9.2,9.9,10.6,11.3,12,12.7,13.4,14.1,14.8,15.6,16.3,17,17.7,18.4,19.1,19.8,20.5,21.2,21.9,22.6]
    ND=[-22.6,-21.9,-21.2,-20.5,-19.8,-19.1,-18.4,-17.7,-17,-16.3,-15.6,-14.8,-14.1,-13.4,-12.7,-12,-11.3,-10.6,-9.9,-9.2,-8.5,-7.8,-7.1,-6.4,-5.7,-4.9,-4.2,-3.5,-2.8,-2.1,-1.4,0,1.4,2.1,2.8,3.5,4.2,4.9,5.7,6.4,7.1,7.8,8.5,9.2,9.9,10.6,11.3,12,12.7,13.4,14.1,14.8,15.6,16.3,17,17.7,18.4,19.1,19.8,20.5,21.2,21.9,22.6]
    PDX=np.dot(PD, np.cos(pi/4))
    PDY=np.dot(PD, np.sin(pi/4))

    QuadWedgeCal=[0.5096,0,0,0,0,0,0,0,0] # 6xqw,15xqw,6fffqw,10fffqw,6eqw,9eqw,12eqw,16eqw,20eqw



    NDX= np.dot( ND , np.cos(pi/4+pi/2))
    NDY= np.dot( ND, np.sin(pi/4+pi/2) )

    # figs = [] #in this list we will hold all the figures


    print('Timetic=',Timetic*1e-6,df['TIMETIC']) # duration of the measurement
    # print('Backrate',df)


    # For FFF data
    k=5
    for column in df.columns[5:68]: #this section records the X axis (-)
        CorrCountXvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)#the corrected data for leakage = Timetic*Bias*Calibration/Gain
        BiasX.append(df[column][0]) # already used in the formula above but saving them just in case
        CalibX.append(df[column][1])
        RawCountXvect.append(df[column][3])
        k=k+1

    for column in df.columns[68:133]: #this section records the Y axis (|)
        CorrCountYvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
        BiasY.append(df[column][0]) # already used in the formula above but saving them just in case
        CalibY.append(df[column][1])
        RawCountYvect.append(df[column][3])
        k=k+1

    for column in df.columns[133:196]: #this section records the D1 axis  (/)
        CorrCountPDvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
        BiasPD.append(df[column][0]) # already used in the formula above but saving them just in case
        CalibPD.append(df[column][1])
        RawCountPDvect.append(df[column][3])
        k=k+1

    for column in df.columns[196:259]: #this section records the D2 axis  (\)
        CorrCountNDvect.append((df[column][3] - Timetic*df[column][0])*df[column][1]/gain)
        BiasND.append(df[column][0]) # already used in the formula above but saving them just in case
        CalibND.append(df[column][1])
        RawCountNDvect.append(df[column][3])
        k=k+1


    #Temporary figure placement
    # fig=plt.figure(figsize=(20, 15))
    fig=plt.figure()
    # gs = gridspec.GridSpec(2, 1, width_ratios=[20,10], height_ratios=[10,5])
    # ax=fig.add_subplot(1,2,1,projection='3d')
    ax=Axes3D(fig)
    ax.scatter(X,np.zeros(len(X)),CorrCountXvect,label='X profile')
    ax.scatter(np.zeros(len(Y)),Y,CorrCountYvect,label='Y profile')
    ax.scatter(PDX,PDY,CorrCountPDvect,label='PD profile')
    ax.scatter(NDX,NDY,CorrCountNDvect,label='ND profile')
    ax.set_xlabel('X distance [cm]')
    ax.set_ylabel('Y distance [cm]')
    ax.legend(loc='upper left')
    # ax.set_title('Energy Mode = '+str(energy)+beamtype)
    ax.set_title(filename)
    # plt.show()

    # figs.append(fig) # we will return for now only one figure

    # see the manual for the following calculations


    FRGN=80
    xli,xri, xlFRGN, xrFRGN,CMX = int_detc_indx(CorrCountXvect,FRGN)
    yli,yri,ylFRGN, yrFRGN,CMY = int_detc_indx(CorrCountYvect,FRGN)

    print('xli,xri, xlFRGN, xrFRGN,CMX')
    print(xli,xri, xlFRGN, xrFRGN,CMX)

    print('yli,yri, ylFRGN, yrFRGN,CMY')
    print(yli, yri, ylFRGN, yrFRGN, CMY)






    #here we calculate the unflatness
    central_value = float(CorrCountXvect[31])
    # print('these must be equal=',CorrCountXvect[31],CorrCountYvect[32])
    unflatness_x = float(2* CorrCountXvect[len(CorrCountXvect)//2] /(CorrCountXvect[8]+CorrCountXvect[54]))  # calculating unflatness in the Transverse - X direction (using -12 and 12)
    unflatness_y = float(2* CorrCountYvect[len(CorrCountYvect)//2] /(CorrCountYvect[8]+CorrCountYvect[56]))  # calculating unflatness in the Radial - Y direction
    print('unflatness(x)=',unflatness_x,'unflatness(y)=',unflatness_y)

    #flatness calculation by variance, remember these ranges are assuming a field size of 30X30
    # print(len(CorrCountXvect))
    # print(CorrCountXvect,np.amax(CorrCountXvect[8:54]),np.amin(CorrCountXvect[8:54]))
    flatness_x = 100*(np.amax(CorrCountXvect[xli:xri+1])-np.amin(CorrCountXvect[xli:xri+1]))/(np.amax(CorrCountXvect[xli:xri+1])+np.amin(CorrCountXvect[xli:xri+1]))  # calculating flatness in the Transverse - X direction
    flatness_y = 100*(np.amax(CorrCountYvect[yli:yri+1])-np.amin(CorrCountYvect[yli:yri+1]))/(np.amax(CorrCountYvect[yli:yri+1])+np.amin(CorrCountYvect[yli:yri+1]))  # calculating flatness in the Radial - Y direction (It has a couple of more sensors in -0.5 and 0.5)
    # print(len(CorrCountXvect),'data=',CorrCountXvect[59],'unflatness_x=',unflatness_x,'unflatness_y=',unflatness_y, 'flatness_x=', flatness_x, 'flatness_y=', flatness_y)

    print('flatness(x)=',flatness_x,'flatness(y)=',flatness_y)


    Xi = []  # these two vectors hold the index location of each detector
    for i, v in enumerate(CorrCountXvect):
        # print(i, v)
        Xi.append(i)

    Yi = []
    for i, v in enumerate(CorrCountYvect):
        # print(i, v)
        Yi.append(i)






    # here we calculate the symmetry (This code is equivalent to SYMA - see documentation)
    # for the X

    area_R_X = area_calc(CorrCountXvect[int(CMX):xri+1], Xi[int(CMX):xri+1])
    area_L_X = area_calc(CorrCountXvect[xli:int(CMX)+1], Xi[xli:int(CMX)+1])

    # print('1','area_L_X','area_R_X')
    # print(area_L_X,area_R_X)
    #
    mCMX = (CorrCountXvect[int(CMX)+1] - CorrCountXvect[int(CMX)]) / (int(CMX)+1 - int(CMX))
    fCMX = CorrCountXvect[int(CMX)] + (CMX-int(CMX))*mCMX
    areaCMX = 1/2 * (fCMX+CorrCountXvect[int(CMX)]) * (CMX-int(CMX))
    # print(CMX, int(CMX), areaCMX)
    #
    ml = (CorrCountXvect[xli]-CorrCountXvect[xli-1]) / (xli-(xli-1))
    fxlFRGN = CorrCountXvect[xli-1] + (xlFRGN-(xli-1))*ml
    # print(fxlFRGN,CorrCountXvect[xli-1])
    areaExL = 1/2 * (fxlFRGN + CorrCountXvect[xli]) * (xli-xlFRGN)
    area_L_X = area_L_X + areaCMX + areaExL
    #
    mr = (CorrCountXvect[xri+1]-CorrCountXvect[xri]) / (xri+1-xri)
    fxrFRGN = CorrCountXvect[xri] + (xrFRGN-(xri))*mr
    # print(fxrFRGN,CorrCountXvect[xri])
    areaExR = 1 / 2 * (fxrFRGN + CorrCountXvect[xri]) * (xrFRGN - xri)
    area_R_X = area_R_X - areaCMX + areaExR
    #
    # print('areaExL','areaExR','areaCMX')
    # print(areaExL,areaExR,areaCMX)
    # print('2','area_L_X','area_R_X')
    # print(area_L_X,area_R_X)

    # fig,ax = plt.subplots()
    # ax.scatter(Xi,CorrCountXvect)
    # ax.scatter(xli,CorrCountXvect[xli],label='xli')
    # ax.scatter(xlFRGN,fxlFRGN,label='xlFRGN')
    # ax.scatter(xri,CorrCountXvect[xri],label='xri')
    # ax.scatter(xrFRGN,fxrFRGN,label='xrFRGN')
    # ax.scatter(int(CMX),CorrCountXvect[int(CMX)],label='int(CMX)')
    # ax.scatter(CMX,fCMX,label='CMX')
    # ax.set_title('X')
    # ax.legend()
    #
    # fig,ax = plt.subplots()
    # print(len(CorrCountXvect) // 2)
    # # ax.scatter(Xi[len(CorrCountXvect) // 2:xri+1],CorrCountXvect[len(CorrCountXvect) // 2:xri+1])
    # ax.scatter(Xi[xli:int(CMX)+1],CorrCountXvect[xli:int(CMX)+1])
    # ax.set_title('X')
    # ax.legend()


    symmetry_X = 200 * (area_R_X - area_L_X) / (area_L_X + area_R_X)
    print('Symmetry_X=', symmetry_X)



    #for the Y # KEEP WORKING HERE!
    area_R_Y = area_calc(CorrCountYvect[int(CMY):yri+1], Yi[int(CMY):yri+1])
    area_L_Y = area_calc(CorrCountYvect[yli:int(CMY)+1], Yi[yli:int(CMY)+1])

    # print('area_R_Y',area_R_Y)
    # print('area_L_Y',area_L_Y)


    symmetry_Y = 200 * (area_R_Y - area_L_Y) / (area_L_Y + area_R_Y)
    # symmetry_Y = 100*(CorrCountYvect[8]-CorrCountYvect[57])/CorrCountYvect[int(len(CorrCountYvect) / 2)]
    # print('Symmetry_Y_nocorr=', symmetry_Y)


    mCMY = (CorrCountYvect[int(CMY)+1] - CorrCountYvect[int(CMY)]) / (int(CMY)+1 - int(CMY))
    fCMY = CorrCountYvect[int(CMY)] + (CMY-int(CMY))*mCMY
    areaCMY = 1/2 * (fCMY+CorrCountYvect[int(CMY)]) * (CMY-int(CMY))

    #
    ml = (CorrCountYvect[yli]-CorrCountYvect[yli-1]) / (yli-(yli-1))
    fylFRGN = CorrCountYvect[yli-1] + (ylFRGN-(yli-1))*ml
    areaEyL = 1/2 * (fylFRGN + CorrCountYvect[yli]) * (yli-ylFRGN)
    area_L_Y = area_L_Y + areaCMY + areaEyL
    #
    mr = (CorrCountYvect[yri+1]-CorrCountYvect[yri]) / (yri+1-yri)
    fyrFRGN = CorrCountYvect[yri] + (yrFRGN-(yri))*mr
    areaEyR = 1 / 2 * (fyrFRGN + CorrCountYvect[yri]) * (yrFRGN - yri)
    area_R_Y = area_R_Y - areaCMY + areaEyR



    # print('areaCMY','areaEyL','areaEyR')
    # print(areaCMY,areaEyL,areaEyR)

    # print('area_R_Y', area_R_Y)
    # print('area_L_Y', area_L_Y)

    # fig, ax = plt.subplots()
    # ax.scatter(Yi, CorrCountYvect)
    # ax.scatter(yli, CorrCountYvect[yli], label='yli')
    # ax.scatter(ylFRGN, fylFRGN, label='ylFRGN')
    # ax.scatter(yri, CorrCountYvect[yri], label='yri')
    # ax.scatter(yrFRGN, fyrFRGN, label='yrFRGN')
    # ax.scatter(int(CMY), CorrCountYvect[int(CMY)], label='int(CMY)')
    # ax.scatter(CMY, fCMY, label='CMY')
    # ax.set_title('Y')
    # ax.legend()
    #
    # fig, ax = plt.subplots()
    # ax.scatter(Yi[int(CMY):yri+1],CorrCountYvect[int(CMY):yri+1])
    # ax.set_title('Y_R')
    # fig, ax = plt.subplots()
    # ax.scatter(Yi[yli:int(CMY)+1], CorrCountYvect[yli:int(CMY)+1])
    # ax.set_title('Y_L')
    #
    # ax.legend()
    # plt.show()



    symmetry_Y = 200 * (area_R_Y - area_L_Y) / (area_L_Y + area_R_Y)
    # symmetry_Y = 100*(CorrCountYvect[8]-CorrCountYvect[57])/CorrCountYvect[int(len(CorrCountYvect) / 2)]
    print('Symmetry_Y=', symmetry_Y)

    # np.savetxt('CorrCountYvect.csv',np.asarray(CorrCountYvect),delimiter=',')
    # np.savetxt('Yi.csv',np.asarray(Yi),delimiter=',')
    # np.savetxt('Y.csv',np.asarray(Y),delimiter=',')

    plt.show()
    exit(0)












    if beamtype == 'FFF' and energy == 6:
        CellChange['F52'] = unflatness_y  # "UnflatnessY"
        CellChange['G52'] = unflatness_x  # "UnflatnessX"
        CellChange['F53'] = symmetry_Y  # "SymmetryY"
        CellChange['G53'] = symmetry_X  # "SymmetryX"
        CellChange['H54'] = central_value  # "CentralReading"
        # print('CellChange',CellChange)
        # print('none', CellChange)


    elif beamtype == 'FFF' and energy == 10:
        CellChange['F57'] = unflatness_y  # "UnflatnessY"
        CellChange['G57'] = unflatness_x  # "UnflatnessX"
        CellChange['F58'] = symmetry_Y  # "SymmetryY"
        CellChange['G58'] = symmetry_X  # "SymmetryX"
        CellChange['H60'] = central_value  # "CentralReading"
        # print('CellChange',CellChange)
        # print('none', CellChange)


    elif beamtype == 'X' and energy == 6:
        CellChange['F43'] = flatness_y  # "FlatnessY"
        CellChange['G43'] = flatness_x  # "FlatnessX"
        CellChange['F44'] = symmetry_Y  # "SymmetryY"
        CellChange['G44'] = symmetry_X  # "SymmetryX"
        CellChange['H45'] = central_value  # "CentralReading"
        # print('CellChange',CellChange)
        # print('none', CellChange)


    elif beamtype == 'X' and energy == 15:
        CellChange['F47'] = flatness_y  # "FlatnessY"
        CellChange['G47'] = flatness_x  # "FlatnessX"
        CellChange['F48'] = symmetry_Y  # "SymmetryY"
        CellChange['G48'] = symmetry_X  # "SymmetryX"
        CellChange['H49'] = central_value  # "CentralReading"
        # print('CellChange',CellChange)
        # print('none', CellChange)


    elif beamtype == 'X' and energy == 10:
        CellChange['F46'] = flatness_y  # "FlatnessY"
        CellChange['G46'] = flatness_x  # "FlatnessX"
        CellChange['F47'] = symmetry_Y  # "SymmetryY"
        CellChange['G47'] = symmetry_X  # "SymmetryX"
        # CellChange['H49'] = central_value  # "CentralReading"
        # print('CellChange',CellChange)
        # print('none', CellChange)



    #This section will calculate D10 for photon beams
    if np.sum(np.asarray(CorrCountXvect)-np.asarray(CorrCountPDvect))/1e6 > 5 and (beamtype=='X' or beamtype=='FFF'): #most likely the file is a quad-wedge and we can calculate then D10
        CellChange.clear()
        #correct D = 13.4 -> 4.2,  Main = 14 (13.5) -> 4 (4.5)
        PDArea = np.sum(np.asarray(CorrCountPDvect[13:27]))+np.sum(np.asarray(CorrCountPDvect[36:50]))
        NDArea = np.sum(np.asarray(CorrCountNDvect[13:27])) + np.sum(np.asarray(CorrCountNDvect[36:50]))
        XArea = np.sum(np.asarray(CorrCountXvect[5:24])) + np.sum(np.asarray(CorrCountXvect[39:58]))  # Note that in the manual it is supposed to go from 4->14 but in reality it goes from 4.5->13.5
        YArea = np.sum(np.asarray(CorrCountYvect[5:24])) + np.sum(np.asarray(CorrCountYvect[41:60]))

        AreaRatio=(PDArea+NDArea)/(XArea+YArea)
        # print('AreaRatio=',AreaRatio)



        #energies for TB
        if poption2.startswith(('t', 'truebeam', 'true')):
            if cart=='a':
                if energy==6 and beamtype=='X':
                    m = 151.3453
                    b = -10.1259
                    D10=m*AreaRatio+b
                    CellChange['G67'] = D10
                    Attributes = ['D10']


                if energy==6 and beamtype=='FFF':
                    m = 184.1376
                    b = -30.4054
                    D10=m*AreaRatio+b
                    CellChange['G69'] = D10
                    Attributes = ['D10']

                if energy==15 and beamtype=='X':
                    m = 117.088
                    b = 9.95284
                    D10=m*AreaRatio+b
                    CellChange['G68'] = D10
                    Attributes = ['D10']

                if energy==10 and beamtype=='FFF':
                    m = 143.9148
                    b = -8.4045
                    D10=m*AreaRatio+b
                    CellChange['G70'] = D10
                    Attributes = ['D10']

            elif cart=='b':
                if energy == 6 and beamtype == 'X':
                    m = 151.3453
                    b = -10.7339
                    D10 = m * AreaRatio + b
                    CellChange['G67'] = D10
                    Attributes = ['D10']

                if energy == 6 and beamtype == 'FFF':
                    m = 184.1376
                    b = -30.9800
                    D10 = m * AreaRatio + b
                    CellChange['G69'] = D10
                    Attributes = ['D10']

                if energy == 15 and beamtype == 'X':
                    m = 117.0881
                    b = 10.2143
                    D10 = m * AreaRatio + b
                    CellChange['G68'] = D10
                    Attributes = ['D10']

                if energy == 10 and beamtype == 'FFF':
                    m = 143.9148
                    b = -9.3128
                    D10 = m * AreaRatio + b
                    CellChange['G70'] = D10
                    Attributes = ['D10']



        # energies for Clinacs
        elif poption2.startswith(('c', 'clinac', 'clin')):
            if cart == 'a':
                if energy == 6 and beamtype == 'X':
                    m = 151.3453
                    b = -10.5282
                    D10 = m * AreaRatio + b
                    CellChange['G48'] = D10
                    Attributes = ['D10']


                if energy == 10 and beamtype == 'X':
                    m = 98.1368
                    b = 20.0212
                    D10 = m * AreaRatio + b
                    CellChange['G49'] = D10
                    Attributes = ['D10']

            elif cart == 'b':
                print('cart=',cart)
                if energy == 6 and beamtype == 'X':
                    m = 151.3453
                    b = -11.0944
                    D10 = m * AreaRatio + b
                    CellChange['G48'] = D10
                    Attributes = ['D10']

                if energy == 10 and beamtype == 'X':
                    m = 98.1368
                    b = 19.5740
                    D10 = m * AreaRatio + b
                    CellChange['G49'] = D10
                    Attributes = ['D10']



    # This section will calculate R50 for electron beams
    elif np.sum(np.asarray(CorrCountXvect) - np.asarray(CorrCountPDvect)) / 1e6 > 5 and beamtype == 'MeV':  # most likely the file is a quad-wedge and we can calculate then D10
        CellChange.clear()
        # 4 to 12 (excluding 4 including 12 on both diagonal and horizontal and vertical)
        # correct D = 12 -> 4,  Main = 14 (13.5) -> 4 (4.5)
        PDArea = np.sum(np.asarray(CorrCountPDvect[16:27])) + np.sum(np.asarray(CorrCountPDvect[36:47]))
        NDArea = np.sum(np.asarray(CorrCountNDvect[16:27])) + np.sum(np.asarray(CorrCountNDvect[36:47]))
        XArea = np.sum(np.asarray(CorrCountXvect[9:24])) + np.sum(np.asarray(CorrCountXvect[39:54]))  # Note that in the manual it is supposed to go from 4->14 but in reality it goes from 4.5->13.5
        YArea = np.sum(np.asarray(CorrCountYvect[9:24])) + np.sum(np.asarray(CorrCountYvect[41:56]))

        AreaRatio = (PDArea + NDArea) / (XArea + YArea)


        #there are only electrons for TB
        if energy==6:
            C1 = 1603.73800
            C2 = -537.15500
            C3 = 47.14986
            R50 = C1*AreaRatio*AreaRatio + C2*AreaRatio + C3
            CellChange['G81'] = R50
            CellChange['J89']=central_value
            Attributes = ['R50','Central Value']


        if energy==9:
            C1 = 348.56370
            C2 = -176.65700
            C3 = 25.68557
            R50=C1*AreaRatio*AreaRatio+C2*AreaRatio+C3
            CellChange['G82'] = R50
            CellChange['J90'] = central_value
            Attributes = ['R50','Central Value']

        if energy==12:
            C1 = 142.14400
            C2 = -109.24300
            C3 = 25.71886
            R50=C1*AreaRatio*AreaRatio+C2*AreaRatio+C3
            CellChange['G83'] = R50
            CellChange['J91'] = central_value
            Attributes = ['R50','Central Value']


        if energy==16:
            C1 = 325.17690
            C2 = -335.77100
            C3 = 92.92214
            R50=C1*AreaRatio*AreaRatio+C2*AreaRatio+C3
            CellChange['G84'] = R50
            CellChange['J92'] = central_value
            Attributes = ['R50','Central Value']


        if energy==20:
            C1 = 734.65730
            C2 = -873.04600
            C3 = 267.15960
            R50=C1*AreaRatio*AreaRatio+C2*AreaRatio+C3
            CellChange['G85'] = R50
            CellChange['J93'] = central_value
            Attributes = ['R50','Central Value']






    #this section will verify that the field size is 30x30
    #now doing the X axis (transverse)
    XRes=np.linspace(-16,16,1000)
    CorrCountXvectRes = np.interp(XRes,X, CorrCountXvect)
    CorrCountXvectResDiff=signal.savgol_filter(np.diff(CorrCountXvectRes),71,5)

    peak1, _ = find_peaks(CorrCountXvectResDiff, prominence=5000)
    peak2, _ = find_peaks(-CorrCountXvectResDiff, prominence=5000)

    if round(XRes[int(peak2)] - XRes[int(peak1)])!=30:
        print("WARNING: X Field is not setup correctly.")



    #now doing the Y axis (inline)
    YRes=np.linspace(-16,16,1000)
    CorrCountYvectRes = np.interp(YRes,Y, CorrCountYvect)
    CorrCountYvectResDiff=signal.savgol_filter(np.diff(CorrCountYvectRes),71,5)

    peak1, _ = find_peaks(CorrCountYvectResDiff, prominence=5000)
    peak2, _ = find_peaks(-CorrCountYvectResDiff, prominence=5000)

    if round(YRes[int(peak2)] - YRes[int(peak1)])!=30:
        print("WARNING: Y Field is not setup correctly.")















    # print('Here',filename,CellChange,Attributes)


    return CellChange,fig, energy, beamtype, Attributes

    # exit(0)







if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # pylint: disable = invalid-name
    parser.add_argument( "file", help="path to file")
    args = parser.parse_args()  # pylint: disable = invalid-name

    if args.file:
        filename = args.file  # pylint: disable = invalid-name
        read_icp(filename)












