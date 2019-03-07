#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""


#import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import re, get_image_size

executor = ThreadPoolExecutor(max_workers=30)


def readAnnotationFile(annotationFile):
    def splitanno(instr):
        return re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', instr)

    with open(annotationFile,'r') as fid:
        annotationlist = fid.readlines()
    #annotationlist = [x.split(sep) for x in annotationlist]
    annotationlist = [splitanno(x) for x in annotationlist]

    return annotationlist


def kitti2AU(kittyAnnotationList, imsize=None, filename=None, cropbboxtoimage=False):
# AU format: # a JSON-string of the following format
# {
# 'label':<classlabel>,   # a label without spaces
# 'imagepath':<imagepath>,  # relative path to image
# 'imagewidth':<image width>,  # width of image
# 'imageheight':<image height>,  # height of image
# 'xmin': <xmin>,  # minimum column coordinate staring from upper left corner
# 'ymin': <ymin>,  # maximum column coordinate staring from upper left corner
# 'xmax': <xmax>,  # minimum row coordinate staring from upper left corner
# 'ymax': <ymax>,  # maximum row coordinate staring from upper left corner
# 'orientation':<rotation [0:1]>,
# 'occlusion':<occlusion>
# }

############# Arguments:
# kittyAnnotationList list of rows from kitti annotation
# imsize: size of image

    AUannotation=     {
 'label':'',   # a label without spaces
 'imagepath':'',  # relative path to image
 'imagewidth':0,  # width of image
 'imageheight':0,  # height of image
 'xmin': 0,  # minimum column coordinate staring from upper left corner
 'ymin': 0,  # maximum column coordinate staring from upper left corner
 'xmax': 0,  # minimum row coordinate staring from upper left corner
 'ymax': 0,  # maximum row coordinate staring from upper left corner
 'orientation':0.0,
 'occlusion':0
 }
    AUannotationlist = []
    for KittiAnnotation in kittyAnnotationList:
        #splitannotation = KittiAnnotation.split()

        #Split the string at spaces, but respect quotes in specie's names
        #splitannotation = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', KittiAnnotation)

        if not imsize:
            if not filename:
                #defaults to [2048,2448,3]
                imsize=[2048,2448,3] #height, witdh, channels
            else:
                width, height = get_image_size.get_image_size(filename)
                imsize = [height, width, 3]


        objectclass=KittiAnnotation[0]
        xmin=KittiAnnotation[4]
        ymin=KittiAnnotation[5]
        xmax=KittiAnnotation[6]
        ymax=KittiAnnotation[7]


        if cropbboxtoimage:
            xmin = float(max(0,int(xmin)))
            ymin = float(max(0,int(ymin)))
            xmax = float(min(imsize[1]-1,int(xmax)))
            ymax = float(min(imsize[0]-1,int(ymax)))

            assert(xmin>=0)
            assert(ymin>=0)
            assert(xmax<=imsize[1])
            assert(ymax<=imsize[0])

        anno_tmp = AUannotation.copy()
        anno_tmp['label']=objectclass
        anno_tmp['xmin']=xmin
        anno_tmp['xmax']=xmax
        anno_tmp['ymin']=ymin
        anno_tmp['ymax']=ymax
        anno_tmp['imagepath']=filename


        AUannotationlist.append(anno_tmp)

    return AUannotationlist
