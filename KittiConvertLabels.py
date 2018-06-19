#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=50)

inputlabelpath = '/mnt/ST_SPGroup/Projekter/2017RoboWeedMaps/WeedInstanceDetection/Images/KittiAnnotationsOneDir/Labels'





#removelabels = ['en'] #
removelabels = [] #


csvdict = pd.read_csv('Ukrudtsarter i PVO til IGIS.CSV',delimiter=';')
csvdict = csvdict.set_index('Navn').to_dict()


annotationFiles = []
for root, dirnames, filenames in os.walk(inputlabelpath):
    for filename in filenames:
        if filename.lower().endswith(('.txt')):
            annotationFiles.append(os.path.join(root, filename))



#common directory used for defining expor dir
commonpath = os.path.commonpath(annotationFiles)


def convertLabel(annotationFile):
    annotaion = pd.read_csv(annotationFile,delimiter=' ',header=None)

    annotaion[0] = annotaion.apply(lambda row: csvdict['EnToKimbladet'][row[0]],axis=1)

    #Remove species that we don't care about
    if len(annotaion)>0:
        for rl in removelabels:
            annotaion = annotaion[annotaion[0] != rl]

    filename = os.path.basename(annotationFile)
    exportpath = os.path.join(os.path.dirname(commonpath),'EnToKimbladet',filename)

    annotaion.to_csv(exportpath, header=False, index=False, sep=' ')


for annotationFile in annotationFiles:
    '''
    annotaion = pd.read_csv(annotationFile,delimiter=' ',header=None)

    annotaion[0] = annotaion.apply(lambda row: csvdict['EnToKimbladet'][row[0]],axis=1)

    #Remove species that we don't care about
    if len(annotaion)>0:
        for rl in removelabels:
            annotaion = annotaion[annotaion[0] != rl]

    filename = os.path.basename(annotationFile)
    exportpath = os.path.join(os.path.dirname(commonpath),'EnToKimbladet',filename)

    annotaion.to_csv(exportpath, header=False, index=False, sep=' ')
    '''

    a = executor.submit(convertLabel, annotationFile)


executor.shutdown(wait=True)
