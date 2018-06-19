#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

import kitti2voc

import os
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=30)

CROPBBOXTOIMAGE = True


kittidir = '/mnt/ST_SPGroup/Projekter/2017RoboWeedMaps/WeedInstanceDetection/Images/KittiAnnotationsOneDir/EnToKimbladet'
exportdir = '/mnt/ST_SPGroup/Projekter/2017RoboWeedMaps/WeedInstanceDetection/Images/KittiAnnotationsOneDir/Annotations'



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
    kitti2voc.convertAnnotationFile(annotationFile,exportdir)
    #executor.submit(kitti2voc.convertAnnotationFile,annotationFile,exportdir)

executor.shutdown(wait=True)
