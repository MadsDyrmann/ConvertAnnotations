#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""


#import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ET
import os
from concurrent.futures import ThreadPoolExecutor
import struct, imghdr, re
import re, get_image_size

executor = ThreadPoolExecutor(max_workers=30)

CROPBBOXTOIMAGE = True



#convert a list of kitti-annotations to a tree of VOC
def kitti2voc(kittyAnnotationList, imsize=None, filename=None):
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = "VOC2007"


    for KittiAnnotation in kittyAnnotationList:
        #splitannotation = KittiAnnotation.split()

        #Split the string at spaces, but respect quotes in specie's names
        splitannotation = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', KittiAnnotation)





        imageobject = ET.SubElement(annotation, "object")
        ET.SubElement(imageobject, "name").text = splitannotation[0].replace('"','')
        ET.SubElement(imageobject, "pose").text = 'frontal'
        ET.SubElement(imageobject, "truncated").text = 0
        ET.SubElement(imageobject, "difficult").text = 0


        if not imsize:
            if not filename:
                #defaults to [2048,2448,3]
                imsize=[2048,2448,3] #height, witdh, channels
            else:
                #height, width = get_image_size(filename)
                width, height = get_image_size.get_image_size(filename)
                imsize = [height, width, 3]

        sz = ET.SubElement(annotation, "size")
        ET.SubElement(sz, "width").text = str(imsize[1])
        ET.SubElement(sz, "height").text = str(imsize[0])
        ET.SubElement(sz, "depth").text = str(imsize[2])


        bndbox = ET.SubElement(imageobject, "bndbox")
        xmin=splitannotation[4]
        ymin=splitannotation[5]
        xmax=splitannotation[6]
        ymax=splitannotation[7]

        if CROPBBOXTOIMAGE:
            xmin = str(max(0,int(xmin)))
            ymin = str(max(0,int(ymin)))
            xmax = str(min(imsize[1]-1,int(xmax)))
            ymax = str(min(imsize[0]-1,int(ymax)))

            assert(float(xmin)>=0)
            assert(float(ymin)>=0)
            assert(float(xmax)<=imsize[1])
            assert(float(ymax)<=imsize[0])

        ET.SubElement(bndbox, "xmin").text = xmin
        ET.SubElement(bndbox, "ymin").text = ymin
        ET.SubElement(bndbox, "xmax").text = xmax
        ET.SubElement(bndbox, "ymax").text = ymax

    tree = ET.ElementTree(annotation)
    #xmlstr = ET.ElementTree.tostring(annotation, encoding='utf8', method='xml')

    return tree


def convertAnnotationFile(annotationFile,exportdir):
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = "VOC2007"

    with open(annotationFile,'r') as f:
        KittiAnnotations = f.readlines()

    tree = kitti2voc(KittiAnnotations)
    '''
    for KittiAnnotation in KittiAnnotations:
        splitannotation = KittiAnnotation.split()

        imageobject = ET.SubElement(annotation, "object")
        ET.SubElement(imageobject, "name").text = splitannotation[0]
        ET.SubElement(imageobject, "pose").text = 'frontal'
        ET.SubElement(imageobject, "truncated").text = 0
        ET.SubElement(imageobject, "difficult").text = 0

        sz = ET.SubElement(annotation, "size")
        ET.SubElement(sz, "width").text = str(imsize['width'])
        ET.SubElement(sz, "height").text = str(imsize['height'])
        ET.SubElement(sz, "depth").text = str(imsize['depth'])


        bndbox = ET.SubElement(imageobject, "bndbox")
        xmin=splitannotation[4]
        ymin=splitannotation[5]
        xmax=splitannotation[6]
        ymax=splitannotation[7]

        if CROPBBOXTOIMAGE:
            xmin = str(max(0,int(xmin)))
            ymin = str(max(0,int(ymin)))
            xmax = str(min(imsize['width']-1,int(xmax)))
            ymax = str(min(imsize['height']-1,int(ymax)))

            assert(float(xmin)>=0)
            assert(float(ymin)>=0)
            assert(float(xmax)<=imsize['width'])
            assert(float(ymax)<=imsize['height'])

        ET.SubElement(bndbox, "xmin").text = xmin
        ET.SubElement(bndbox, "ymin").text = ymin
        ET.SubElement(bndbox, "xmax").text = xmax
        ET.SubElement(bndbox, "ymax").text = ymax

    tree = ET.ElementTree(annotation)
    '''
    filename = os.path.basename(annotationFile)
    savedir = os.path.join(exportdir,filename.replace('txt','xml'))
    tree.write(savedir, encoding="UTF-8")


