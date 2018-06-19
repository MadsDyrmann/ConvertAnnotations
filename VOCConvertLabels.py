#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=100)
import xml.etree.ElementTree as ET

inputlabelpath = '/mnt/ST_SPGroup/Projekter/2017RoboWeedMaps/WeedInstanceDetection/Images20180322/LocalizationAnnotationsOnedir/VocAnnotations'

#removelabels = ['en'] #
removelabels = ['Unsorted','Junk','1PLAK', '3UNCLK'] #

#Konvert fra dansk navn til  til en eller to-kimbladet
csvdict = pd.read_csv('Ukrudtsarter i PVO til IGIS.CSV',delimiter=';')
csvdict = csvdict.set_index('Navn').to_dict()

#Konvert fra eppo til en eller to-kimbladet
csvdict = pd.read_excel('/media/mads/Data/AU/Database/Ukrudtslisten2.xlsx')
csvdict = csvdict[['eppocode','EnToKimbladet']].set_index('eppocode').to_dict()


annotationFiles = []
for root, dirnames, filenames in os.walk(inputlabelpath):
    for filename in filenames:
        if filename.lower().endswith(('.xml')):
            annotationFiles.append(os.path.join(root, filename))



#common directory used for defining expor dir
commonpath = os.path.commonpath(annotationFiles)

def createIfNotExist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def convertLabel(annotationFile):
    tree = ET.parse(annotationFile)
    root = tree.getroot()

    for annot in root.iter('annotation'):
        for obj in annot.iter('object'):
            for name in obj.iter('name'):
                if name.text in removelabels:
                    annot.remove(obj)
                else:
                    #Assert the label is present in the dictionary
                    if pd.isna(csvdict['EnToKimbladet'][name.text]): raise Exception( name.text + ' not defined in dict' )

                    name.text = csvdict['EnToKimbladet'][name.text]



    filename = os.path.basename(annotationFile)

    createIfNotExist(os.path.join(os.path.dirname(commonpath),'VocAnnotationsEnTO'))
    exportpath = os.path.join(os.path.dirname(commonpath),'VocAnnotationsEnTO',filename)

    assert not os.path.exists(exportpath)

    tree.write(exportpath)


for ix, annotationFile in enumerate(annotationFiles):

    #NB: der er problemer med at ikke alle billeder kommer over, når jeg kører parallelt. Det går også hurtigt uden, så drop for nuværende

    #a = executor.submit(convertLabel, annotationFile)
    print('image '+str(ix)+' of '+str(len(annotationFiles)))
    convertLabel(annotationFile)

executor.shutdown(wait=True)
