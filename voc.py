#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""

from xml.dom import minidom
import os


#define where the VOC annotations are
xmldir = '/media/mads/Data/Testdataset/VOCdevkit/VOC2012/Annotations'
#And where the kitti annotations are to be exported
exportdir = '/media/mads/Data/Testdataset/VOCdevkit/VOC2012/KittiAnnotations'



xmlFiles = []
for root, dirnames, filenames in os.walk(xmldir):
    for filename in filenames:
        if filename.lower().endswith(('.xml')):
            xmlFiles.append(os.path.join(root, filename))

#Set true to use a numerical label
TRANSLATE2NUMERICAL=True

dictionary2integer= {'background':'0',
                     'aeroplane':'1',
                     'bicycle':'2',
                     'bird':'3',
                     'boat':'4',
                     'bottle':'5',
                     'bus':'6',
                     'car':'7',
                     'cat':'8',
                     'chair':'9',
                     'cow':'10',
                     'diningtable':'11',
                     'dog':'12',
                     'horse':'13',
                     'motorbike':'14',
                     'person':'15',
                     'pottedplant':'16',
                     'sheep':'17',
                     'sofa':'18',
                     'train':'19',
                     'tvmonitor':'20'
}


#Run through all xml files
for xmlfile in xmlFiles:

    doc = minidom.parse(xmlfile)

    #Create an empty list of annotaions for each image
    listofkittiannotations = []

    # Get all objects in xml file and loop through them
    objects = doc.getElementsByTagName("object")
    for obj in objects:

        annotation=['class', '0', '3', '0', 'xmin', 'ymin', 'xmax', 'ymax', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']
        ObjClass = obj.getElementsByTagName("name")[0]
        bndbox = obj.getElementsByTagName("bndbox")[0]

        ObjClass = ObjClass.firstChild.data

        #Get the bounding box for that object
        xmin = bndbox.getElementsByTagName("xmin")[0].firstChild.data
        xmax = bndbox.getElementsByTagName("xmax")[0].firstChild.data
        ymin = bndbox.getElementsByTagName("ymin")[0].firstChild.data
        ymax = bndbox.getElementsByTagName("ymax")[0].firstChild.data

        annotation[0]=ObjClass
        annotation[4]=xmin
        annotation[5]=ymin
        annotation[6]=xmax
        annotation[7]=ymax

        if TRANSLATE2NUMERICAL:
            annotation[0]=dictionary2integer[ObjClass]


        listofkittiannotations.append(annotation)

    #Export
    filename = os.path.basename(xmlfile)
    with open(os.path.join(exportdir,filename.replace('xml','txt')),'w') as f:
        f.writelines('\n'.join([' '.join(x) for x in listofkittiannotations]))
