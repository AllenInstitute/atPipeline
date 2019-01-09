# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 17:10:44 2017

@author: olgag
"""
#Calculate scale_factor for all channels in specified session
import os
import numpy as np
import argparse
from skimage.morphology import disk
import cv2
import tifffile
import csv
import configparser
from deconvtools import deconvlucy

parser = argparse.ArgumentParser(description = 'Calculate scale_factor for deconvolution')
parser.add_argument('--drive', help='Name of drive where raw data is located (required)',
                    required=True)
parser.add_argument('--project', help='Project name (required)', required=True)
parser.add_argument('--ribbon', help='RibbonXXXX (required)', required=True)
parser.add_argument('--session', help='sessionXX (raw data) (required)', required=True)                
parser.add_argument('--section', help='Section number (required)', type=int, required=True)   

args = parser.parse_args()

session_directory = os.path.join(args.drive,'data',args.project,'raw',
                                    'data',args.ribbon,args.session)
#session_directory = 'Z:\\data\\S3_Run1_Jarvis\\raw\\data\\Ribbon0068\\session01\\'    
print "session_directory", session_directory

channels = [ch for ch in os.listdir(session_directory) if not ch.endswith('txt')]

def getPSF(filename):
    psf = tifffile.imread(filename)
    psf = psf.astype(float)
    psf = psf/np.sum(psf)
    return psf

def process_tile(inputfile, psf, num_iter, bgrd_size, scale_factor):
    img = tifffile.imread(inputfile)
    img = img.astype(float)
    
    #subtract background
    if not bgrd_size == 0:
         img = cv2.morphologyEx(img,cv2.MORPH_TOPHAT,disk(bgrd_size))
    
    #apply deconvolution
    img_dec = deconvlucy(img, psf, num_iter)
    
    img_dec = img_dec/scale_factor
    sf = np.max(img_dec)/65535 #scale factor
    select = np.nonzero(np.ravel(img_dec)>65535)
    pxl_count = len(select[0]) #number of saturated pxls
    img_dec[img_dec > 65535] = 65535
    return sf, pxl_count

# Write scale_factor data to csv file
def write_sf_data(outdir, channel, sf_list, pxl_count_list, select_files):
    if not os.path.isdir(outdir):
                    os.makedirs(outdir) 
    fname = channel + '_scale_factor.csv'
    filename = os.path.join(outdir, fname)
    f = open(filename, 'wb')
    csvwrite = csv.writer(f, delimiter=',')
    csvwrite.writerow(['channel','scale_factor max','scale_factor min', 
                       'scale_factor median','pxl_count max','pxl_count min',
                       'pxl_count median'])  
    csvwrite.writerow([channel,np.max(sf_list),np.min(sf_list),np.median(sf_list),
                       np.max(pxl_count_list),np.min(pxl_count_list),
                       np.median(pxl_count_list)])
    csvwrite.writerow(['frame','scale_factor','pxl_count'])
    for i in range(len(select_files)):
        csvwrite.writerow([i,sf_list[i],pxl_count_list[i]])  
    f.close()    

for ch in channels:
    data_directory = os.path.join(session_directory, ch)
    print data_directory
    
    data_files =  [f for f in os.listdir(data_directory) if f.endswith('.tif') ] 

    #Select files from specified section
    select_files = []
    for filename in data_files:
        f = os.path.splitext(filename)[0]
        (f,part,frame)=f.partition('_F')
        (f,part,section)=f.partition('_S')
        if int(section) == args.section:
            select_files.append(filename)
    select_files.sort()

    psf_directory = os.path.join(args.drive,'data',args.project,'processed','psfs')
    #psf_directory = 'X:\\data\\M335503_Ai139_smallvol\\processed\\psfs\\'
    if ch[:4] =="DAPI":
        str_psf = 'psf_' + ch[:4] + '.tif' 
    else:
        str_psf = 'psf_' + ch + '.tif'
    psf_file = os.path.join(psf_directory, str_psf)
    print "psf_file", psf_file
    num_iter = 20
    bgrd_size = 20
    scale_factor = 1
    psf = getPSF(psf_file)
    if (ch =='GFP' or ch == 'TdTomato'):
        bgrd_size = 50
    print "bgrd_size", bgrd_size    
    sf_list = []
    pxl_count_list =[]
    for filename in select_files:
        inputfile = os.path.join(data_directory, filename)
        sf, pxl_count = process_tile(inputfile, psf, num_iter, bgrd_size, scale_factor)
        sf_list.append(sf)
        pxl_count_list.append(pxl_count)
    print "channel", ch
    print "sf_list", sf_list
    print "pxl_count_list", pxl_count_list
    print "scale_factor: max %.2f, min %.2f, median %.2f"%(np.max(sf_list), np.min(sf_list),                            
                                                     np.median(sf_list))
    print "number of saturated pxls: max %d, min %d, median %d"%(np.max(pxl_count_list), 
                np.min(pxl_count_list), np.median(pxl_count_list))

    outdir = os.path.join(args.drive,'data',args.project,'processed','deconv_scale_factors')
    #outdir = 'X:\\data\\M335503_Ai139_smallvol\\processed\\deconv_scale_factors\\
    write_sf_data(outdir, ch, sf_list, pxl_count_list, select_files)

#cd C:\Users\olgag\Documents\Python_Scripts\deconv_scale_factor
#python deconv_scale_factor_session.py --drive Z:\ --project S3_Run1_Jarvis --ribbon Ribbon0068 --session session01 --section 2
#python deconv_scale_factor_session.py --drive W:\ --project M246930_Scnn1a_4_f1 --ribbon Ribbon0000 --session session1 --section 30  
    
