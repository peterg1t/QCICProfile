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
# # 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apacnmhe-2.0")
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
from int_detc_indx import int_detc_indx




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
    Y = (np.linspace(1,65,65)-33)/2
    X = np.delete(np.delete(Y,31),32)
    PD = np.delete(np.delete((np.linspace(1,65,65)-33)/2,31),32)
    ND=PD

    PDX = PD/ np.cos(pi / 4)
    PDY = PD/ np.sin(pi / 4)
    NDX = ND/ np.cos(pi / 4 - pi / 2)
    NDY = ND/ np.sin(pi / 4 - pi / 2)

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
    pdli,pdri,pdlFRGN, pdrFRGN,CMPD = int_detc_indx(CorrCountPDvect,FRGN)
    ndli,ndri,ndlFRGN, ndrFRGN,CMND = int_detc_indx(CorrCountNDvect,FRGN)

    # print('xli,xri, xlFRGN, xrFRGN,CMX')
    # print(xli,xri, xlFRGN, xrFRGN,CMX)
    # print(X[xli],X[xri],X[int(CMX)])

    # print('yli,yri, ylFRGN, yrFRGN,CMY')
    # print(yli, yri, ylFRGN, yrFRGN, CMY)
    # print(Y[yli],Y[yri])

    # print('pdli,pdri, pdlFRGN, pdrFRGN,CMPD')
    # print(pdli, pdri, pdlFRGN, pdrFRGN, CMPD)
    # print(PD[pdli],PD[pdri])

    # print('ndli,ndri, ndlFRGN, ndrFRGN,CMND')
    # print(ndli, ndri, ndlFRGN, ndrFRGN, CMND)
    # print(ND[ndli],ND[ndri])



    #here we calculate the unflatness
    central_value = float(CorrCountXvect[31])
    # print('these must be equal=',CorrCountXvect[31],CorrCountYvect[32])
    unflatness_x = float(2* CorrCountXvect[len(CorrCountXvect)//2] /(CorrCountXvect[8]+CorrCountXvect[54]))  # calculating unflatness in the Transverse - X direction (using -12 and 12)
    unflatness_y = float(2* CorrCountYvect[len(CorrCountYvect)//2] /(CorrCountYvect[8]+CorrCountYvect[56]))  # calculating unflatness in the Radial - Y direction
    print('unflatness(x)=',unflatness_x)
    print('unflatness(y)=',unflatness_y)

    #flatness calculation by variance, remember these ranges are assuming a field size of 30X30
    flatness_x = 100*(np.amax(CorrCountXvect[xli:xri + 1])-np.amin(CorrCountXvect[xli:xri + 1]))/(np.amax(CorrCountXvect[xli:xri + 1])+np.amin(CorrCountXvect[xli:xri + 1]))  # calculating flatness in the Transverse - X direction
    flatness_y = 100*(np.amax(CorrCountYvect[yli:yri + 1])-np.amin(CorrCountYvect[yli:yri + 1]))/(np.amax(CorrCountYvect[yli:yri + 1])+np.amin(CorrCountYvect[yli:yri + 1]))  # calculating flatness in the Radial - Y direction (It has a couple of more sensors in -0.5 and 0.5)
    flatness_pd = 100 * (np.amax(CorrCountPDvect[pdli:pdri + 1]) - np.amin(CorrCountPDvect[pdli:pdri + 1])) / (np.amax(CorrCountPDvect[pdli:pdri + 1]) + np.amin(CorrCountPDvect[pdli:pdri + 1]))  # calculating flatness in the PD direction (It has a couple of more sensors in -0.5 and 0.5)
    flatness_nd = 100 * (np.amax(CorrCountNDvect[ndli:ndri + 1]) - np.amin(CorrCountNDvect[ndli:ndri + 1])) / (np.amax(CorrCountNDvect[ndli:ndri + 1]) + np.amin(CorrCountNDvect[ndli:ndri + 1]))  # calculating flatness in the ND direction (It has a couple of more sensors in -0.5 and 0.5)

    # #flatness calculation by CAX variance
    # flatness_x = 0.5*100*(np.amax(CorrCountXvect[xli:xri + 1])-np.amin(CorrCountXvect[xli:xri+1]))/CorrCountXvect[len(CorrCountXvect)//2]  # calculating flatness in the Transverse - X direction
    # flatness_y = 0.5*100*(np.amax(CorrCountYvect[yli:yri + 1])-np.amin(CorrCountYvect[yli:yri+1]))/CorrCountYvect[len(CorrCountYvect)//2]  # calculating flatness in the Radial - Y direction (It has a couple of more sensors in -0.5 and 0.5)
    # flatness_pd = 0.5*100 * (np.amax(CorrCountPDvect[pdli:pdri + 1]) - np.amin(CorrCountPDvect[pdli:pdri + 1])) / CorrCountPDvect[len(CorrCountPDvect)//2]  # calculating flatness in the PD direction (It has a couple of more sensors in -0.5 and 0.5)
    # flatness_nd = 0.5*100 * (np.amax(CorrCountNDvect[ndli:ndri + 1]) - np.amin(CorrCountNDvect[ndli:ndri + 1])) / CorrCountNDvect[len(CorrCountNDvect)//2]  # calculating flatness in the ND direction (It has a couple of more sensors in -0.5 and 0.5)

    print('flatness(x)=',flatness_x)
    print('flatness(y)=',flatness_y)
    print('flatness(pd)=',flatness_pd)
    print('flatness(nd)=',flatness_nd)


    Xi = []  # these two vectors hold the index location of each detector
    for i, v in enumerate(CorrCountXvect):
        # print(i, v)
        Xi.append(i)

    PDi = []
    for i, v in enumerate(CorrCountPDvect):
        # print(i, v)
        PDi.append(i)

    NDi = []
    for i, v in enumerate(CorrCountNDvect):
        # print(i, v)
        NDi.append(i)

    Yi = []
    for i, v in enumerate(CorrCountYvect):
        # print(i, v)
        Yi.append(i)


    # # # here we calculate the symmetry (CAX Point difference)
    # symmetryXVect = (np.flip(CorrCountXvect) - CorrCountXvect)/CorrCountXvect[len(CorrCountXvect)//2]*100
    # symmetryYVect = (np.flip(CorrCountYvect) - CorrCountYvect)/CorrCountYvect[len(CorrCountYvect)//2]*100
    # # print(CorrCountYvect,'symmetryYVect',symmetryYVect)
    # symmetryPDVect = (np.flip(CorrCountPDvect) - CorrCountPDvect)/CorrCountPDvect[len(CorrCountPDvect)//2]*100
    # symmetryNDVect = (np.flip(CorrCountNDvect) - CorrCountNDvect)/CorrCountNDvect[len(CorrCountNDvect)//2]*100
    # symmetry_X=max(symmetryXVect[xli:len(symmetryXVect)//2],key=abs)
    # symmetry_Y=max(symmetryYVect[yli:len(symmetryYVect)//2],key=abs)
    # symmetry_PD=max(symmetryPDVect[pdli:len(symmetryPDVect)//2],key=abs)
    # symmetry_ND=max(symmetryNDVect[ndli:len(symmetryNDVect)//2],key=abs)
    # # print('amax(symmXVect)',symmetry_X)
    # # print('amax(symmYVect)',symmetry_Y)
    # # print('amax(symmPDVect)',symmetry_PD)
    # # print('amax(symmNDVect)',symmetry_ND)
    # index_sym_X = np.argmax(np.abs(symmetryXVect[xli:len(symmetryXVect)//2]))
    # index_sym_Y = np.argmax(np.abs(symmetryYVect[yli:len(symmetryYVect)//2]))
    # index_sym_PD = np.argmax(np.abs(symmetryPDVect[pdli:len(symmetryPDVect)//2]))
    # index_sym_ND = np.argmax(np.abs(symmetryNDVect[ndli:len(symmetryNDVect)//2]))
    # print(xli,X[xli],'amax(symmXVect)',symmetry_X,index_sym_X,X[xli+index_sym_X])
    # print(yli,Y[yli],'amax(symmYVect)',symmetry_Y,index_sym_Y,Y[yli+index_sym_Y])
    # print(pdli,PD[pdli],'amax(symmPDVect)',symmetry_PD,index_sym_PD,PD[pdli+index_sym_PD])
    # print(ndli,ND[ndli],'amax(symmNDVect)',symmetry_ND,index_sym_ND,ND[ndli+index_sym_ND])

    # exit(0)






    # here we calculate the symmetry (This code is equivalent to SYMA - see documentation)
    # for the X
    print('input to area calculation')
    area_R_X = area_calc(CorrCountXvect[int(CMX):xri + 1], Xi[int(CMX):xri + 1])
    area_L_X = area_calc(CorrCountXvect[xli:int(CMX) + 1], Xi[xli:int(CMX) + 1])
    mCMX = (CorrCountXvect[int(CMX) + 1] - CorrCountXvect[int(CMX)]) / (int(CMX) + 1 - int(CMX))
    fCMX = CorrCountXvect[int(CMX)] + (CMX - int(CMX)) * mCMX
    areaCMX = 1 / 2 * (fCMX + CorrCountXvect[int(CMX)]) * (CMX - int(CMX))
    ml = (CorrCountXvect[xli] - CorrCountXvect[xli - 1]) / (xli - (xli - 1))
    fxlFRGN = CorrCountXvect[xli - 1] + (xlFRGN - (xli - 1)) * ml
    areaExL = 1 / 2 * (fxlFRGN + CorrCountXvect[xli]) * (xli - xlFRGN)
    area_L_X = area_L_X + areaCMX + areaExL
    mr = (CorrCountXvect[xri + 1] - CorrCountXvect[xri]) / (xri + 1 - xri)
    fxrFRGN = CorrCountXvect[xri] + (xrFRGN - (xri)) * mr
    areaExR = 1 / 2 * (fxrFRGN + CorrCountXvect[xri]) * (xrFRGN - xri)
    area_R_X = area_R_X - areaCMX + areaExR

    symmetry_X = 200 * (area_R_X - area_L_X) / (area_L_X + area_R_X)
    print('Symmetry_X=', symmetry_X)


    # for the Y
    area_R_Y = area_calc(CorrCountYvect[int(CMY):yri + 1], Yi[int(CMY):yri + 1])
    area_L_Y = area_calc(CorrCountYvect[yli:int(CMY) + 1], Yi[yli:int(CMY) + 1])
    symmetry_Y = 200 * (area_R_Y - area_L_Y) / (area_L_Y + area_R_Y)
    mCMY = (CorrCountYvect[int(CMY) + 1] - CorrCountYvect[int(CMY)]) / (int(CMY) + 1 - int(CMY))
    fCMY = CorrCountYvect[int(CMY)] + (CMY - int(CMY)) * mCMY
    areaCMY = 1 / 2 * (fCMY + CorrCountYvect[int(CMY)]) * (CMY - int(CMY))
    ml = (CorrCountYvect[yli] - CorrCountYvect[yli - 1]) / (yli - (yli - 1))
    fylFRGN = CorrCountYvect[yli - 1] + (ylFRGN - (yli - 1)) * ml
    areaEyL = 1 / 2 * (fylFRGN + CorrCountYvect[yli]) * (yli - ylFRGN)
    area_L_Y = area_L_Y + areaCMY + areaEyL
    mr = (CorrCountYvect[yri + 1] - CorrCountYvect[yri]) / (yri + 1 - yri)
    fyrFRGN = CorrCountYvect[yri] + (yrFRGN - (yri)) * mr
    areaEyR = 1 / 2 * (fyrFRGN + CorrCountYvect[yri]) * (yrFRGN - yri)
    area_R_Y = area_R_Y - areaCMY + areaEyR

    symmetry_Y = 200 * (area_R_Y - area_L_Y) / (area_L_Y + area_R_Y)
    # symmetry_Y = 100*(CorrCountYvect[8]-CorrCountYvect[57])/CorrCountYvect[int(len(CorrCountYvect) / 2)]
    print('Symmetry_Y=', symmetry_Y)

    # for the PD
    area_R_PD = area_calc(CorrCountPDvect[int(CMPD):pdri + 1], PDi[int(CMPD):pdri + 1])
    area_L_PD = area_calc(CorrCountPDvect[pdli:int(CMPD) + 1], PDi[pdli:int(CMPD) + 1])
    symmetry_PD = 200 * (area_R_PD - area_L_PD) / (area_L_PD + area_R_PD)
    mCMPD = (CorrCountPDvect[int(CMPD) + 1] - CorrCountPDvect[int(CMPD)]) / (int(CMPD) + 1 - int(CMPD))
    fCMPD = CorrCountPDvect[int(CMPD)] + (CMPD - int(CMPD)) * mCMPD
    areaCMPD = 1 / 2 * (fCMPD + CorrCountPDvect[int(CMPD)]) * (CMPD - int(CMPD))
    ml = (CorrCountPDvect[pdli] - CorrCountPDvect[pdli - 1]) / (pdli - (pdli - 1))
    fpdlFRGN = CorrCountPDvect[pdli - 1] + (pdlFRGN - (pdli - 1)) * ml
    areaEpdL = 1 / 2 * (fpdlFRGN + CorrCountPDvect[pdli]) * (pdli - pdlFRGN)
    area_L_PD = area_L_PD + areaCMPD + areaEpdL
    mr = (CorrCountPDvect[pdri + 1] - CorrCountPDvect[pdri]) / (pdri + 1 - pdri)
    fpdrFRGN = CorrCountPDvect[pdri] + (pdrFRGN - (pdri)) * mr
    areaEpdR = 1 / 2 * (fpdrFRGN + CorrCountPDvect[pdri]) * (pdrFRGN - pdri)
    area_R_PD = area_R_PD - areaCMPD + areaEpdR

    symmetry_PD = 200 * (area_R_PD - area_L_PD) / (area_L_PD + area_R_PD)
    print('Symmetry_PD=', symmetry_PD)

    # for the ND
    area_R_ND = area_calc(CorrCountNDvect[int(CMND):ndri + 1], NDi[int(CMND):ndri + 1])
    area_L_ND = area_calc(CorrCountNDvect[ndli:int(CMND) + 1], NDi[ndli:int(CMND) + 1])
    symmetry_ND = 200 * (area_R_ND - area_L_ND) / (area_L_ND + area_R_ND)
    mCMND = (CorrCountNDvect[int(CMND) + 1] - CorrCountNDvect[int(CMND)]) / (int(CMND) + 1 - int(CMND))
    fCMND = CorrCountNDvect[int(CMND)] + (CMND - int(CMND)) * mCMND
    areaCMND = 1 / 2 * (fCMND + CorrCountNDvect[int(CMND)]) * (CMND - int(CMND))
    ml = (CorrCountNDvect[ndli] - CorrCountNDvect[ndli - 1]) / (ndli - (ndli - 1))
    fndlFRGN = CorrCountNDvect[ndli - 1] + (ndlFRGN - (ndli - 1)) * ml
    areaEndL = 1 / 2 * (fndlFRGN + CorrCountNDvect[ndli]) * (ndli - ndlFRGN)
    area_L_ND = area_L_ND + areaCMND + areaEndL
    mr = (CorrCountNDvect[ndri + 1] - CorrCountNDvect[ndri]) / (ndri + 1 - ndri)
    fndrFRGN = CorrCountNDvect[ndri] + (ndrFRGN - (ndri)) * mr
    areaEndR = 1 / 2 * (fndrFRGN + CorrCountNDvect[ndri]) * (ndrFRGN - ndri)
    area_R_ND = area_R_ND - areaCMND + areaEndR

    symmetry_ND = 200 * (area_R_ND - area_L_ND) / (area_L_ND + area_R_ND)
    print('Symmetry_ND=', symmetry_ND)

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












