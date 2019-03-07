#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

import kitti
import CSV

import os

CROPBBOXTOIMAGE = True


kittidir = '/mnt/AU_BrugerDrev/Database/GetThumbnailsFromServerForDetection_242_326_336_249_250_279_2018-05-22/LocalizationAnnotationsOnedir/KittiAnnotations'
exportdir = '/mnt/AU_BrugerDrev/Database/GetThumbnailsFromServerForDetection_242_326_336_249_250_279_2018-05-22/LocalizationAnnotationsOnedir/csvAnnotations'


annotationFiles = []
for root, dirnames, filenames in os.walk(kittidir):
    for filename in filenames:
        if filename.lower().endswith(('.txt')):
            annotationFiles.append(os.path.join(root, filename))


def createIfNotExist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

createIfNotExist(exportdir)


for annotationFile in annotationFiles:
    kittianno=kitti.readAnnotationFile(annotationFile)
    imagepathparts = annotationFile.split(os.path.sep)
    imagepathparts[-2]='JPEGImages' #set image folder
    imagepathparts[-1]=os.path.splitext(imagepathparts[-1])[-2] #remove extension
    imagepathWithoutext=os.path.sep.join(imagepathparts) #construct imagepath without extension
    imagesInDirectory = os.listdir(os.path.sep.join(imagepathparts[:-1]))

    imagepathWithExtension =[x for x in imagesInDirectory if os.path.splitext(x)[0]==imagepathWithoutext]

    AUanno = kitti.kitti2AU(kittianno,filename=annotationFile)
    csvanno = CSV.AU2csv(AUanno)
    CSV.csvlist2file(csvAnnotationList=csvanno,outputpath=exportdir)

    pass