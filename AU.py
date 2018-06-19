#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann

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

# CSV format: # (see retinanet)
# path/to/image.jpg,x1,y1,x2,y2,class_name

############# Arguments:
# AUAnnotationList list of rows from kitti annotation
# imsize: size of image
"""


#import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import os

executor = ThreadPoolExecutor(max_workers=30)


def AU2csv(AUAnnotationList):

    csvAnnotationList = []
    for anno in AUAnnotationList:
        #Split the string at spaces, but respect quotes in specie's names
        csvline = [anno['imagepath'],anno['xmin'],anno['ymin'],anno['xmax'],anno['ymax'],anno['label']]
        csvline = [x if ',' not in x else '"'+x+'"' for x in csvline] # add '"' if comma exist in entry

        csvAnnotationList.append(csvline)
    return csvAnnotationList



def csvlist2file(csvAnnotationList,outputpath=None):
    assert outputpath is not None

    #get unique file-names, as we want a file per image
    imagefiles = [csvline[0] for csvline in csvAnnotationList]
    uniquefilenames = list(set(imagefiles))

    for filename in uniquefilenames:
        annotationlistForImage=[csvline for csvline in csvAnnotationList if csvline[0]==filename]
        annotationStringlist=[csvanno2string(csvline) for csvline in annotationlistForImage]

        filename, ext = os.path.splitext(filename)
        outoutfilepath = os.path.join(outputpath,filename+'.csv')
        with open(outoutfilepath,'w') as fid:
            fid.writelines(annotationStringlist)


def csvanno2string(csvline, sep=','):
    return sep.join(csvline)

