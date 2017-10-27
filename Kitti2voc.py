#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""


import xml.etree.cElementTree as ET
import os



kittidir = '/media/mads/Data/Testdataset/VOCdevkit/VOC2007/KittiAnnotations'
exportdir = '/media/mads/Data/Testdataset/VOCdevkit/VOC2007/AnnoVoc'



annotationFiles = []
for root, dirnames, filenames in os.walk(kittidir):
    for filename in filenames:
        if filename.lower().endswith(('.txt')):
            annotationFiles.append(os.path.join(root, filename))



for annotationFile in annotationFiles:

    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = "VOC2007"


    with open(annotationFile,'r') as f:
        KittiAnnotation = f.readlines()

    for KittiAnnotation in KittiAnnotation:
        splitannotation = KittiAnnotation.split()

        imageobject = ET.SubElement(annotation, "object")
        ET.SubElement(imageobject, "name").text = splitannotation[0]
        ET.SubElement(imageobject, "pose").text = 'frontal'
        ET.SubElement(imageobject, "truncated").text = 0
        ET.SubElement(imageobject, "difficult").text = 0

        bndbox = ET.SubElement(imageobject, "bndbox")
        xmin=splitannotation[4]
        ymin=splitannotation[5]
        xmax=splitannotation[6]
        ymax=splitannotation[7]
        ET.SubElement(bndbox, "xmin").text = xmin
        ET.SubElement(bndbox, "ymin").text = ymin
        ET.SubElement(bndbox, "xmax").text = xmax
        ET.SubElement(bndbox, "ymax").text = ymax

    filename = os.path.basename(annotationFile)
    savedir = os.path.join(exportdir,filename.replace('txt','xml'))
    tree = ET.ElementTree(annotation)
    tree.write(savedir)
