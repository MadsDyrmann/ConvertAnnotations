#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

import kitti
import pandas as pd

import os
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=30)

CROPBBOXTOIMAGE = True


kittidir = '/mnt/AU_BrugerDrev/Database/GetThumbnailsFromServerForDetection_242_326_336_249_250_279_2018-05-22/LocalizationAnnotationsOnedir/KittiAnnotations'
exportdir = '/mnt/AU_BrugerDrev/Database/GetThumbnailsFromServerForDetection_242_326_336_249_250_279_2018-05-22/LocalizationAnnotationsOnedir/AUAnnotations'



annotationFiles = []
for root, dirnames, filenames in os.walk(kittidir):
    for filename in filenames:
        if filename.lower().endswith(('.txt')):
            annotationFiles.append(os.path.join(root, filename))


imsize = {'width':2448,
          'height':2048,
          'depth':3}


def createIfNotExist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

createIfNotExist(exportdir)



for annotationFile in annotationFiles:
    with open(annotationFile,'r') as fid:
        annotationlist = fid.readlines()
        AUannotationList = kitti.kitti2AU(annotationlist, filename=None)
        df = pd.DataFrame(AUannotationList)
        filename, ext = os.path.splitext(os.path.basename(annotationFile))

        df.to_csv(os.path.join(exportdir,filename+'.csv'),sep=';')

