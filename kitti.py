#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""


#import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import re, get_image_size

#import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ET
import os
import struct, imghdr

executor = ThreadPoolExecutor(max_workers=30)

CROPBBOXTOIMAGE = True



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
        if type(KittiAnnotation) is str:
            KittiAnnotation = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', KittiAnnotation)

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




#convert a list of kitti-annotations to yolo-format
# <object-class> <x> <y> <width> <height>, where values are relative to image size
def kitti2yolo(kittyAnnotationList, imsize=None, filename=None):

    def convert(size, box):
        # box xmin, xmax, ymin, ymax
        dw = 1./size[0]
        dh = 1./size[1]
        x = (box[0] + box[1])/2.0
        y = (box[2] + box[3])/2.0
        w = box[1] - box[0]
        h = box[3] - box[2]
        x = x*dw
        w = w*dw
        y = y*dh
        h = h*dh
        return (x,y,w,h)

    yoloannotationlist = []
    for KittiAnnotation in kittyAnnotationList:
        #splitannotation = KittiAnnotation.split()

        #Split the string at spaces, but respect quotes in specie's names
        splitannotation = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', KittiAnnotation)

        if not imsize:
            if not filename:
                #defaults to [2048,2448,3]
                imsize=[2048,2448,3] #height, witdh, channels
            else:
                height, width = get_image_size(filename)
                imsize = [height, width, 3]


        objectclass=splitannotation[0]
        xmin=splitannotation[4]
        ymin=splitannotation[5]
        xmax=splitannotation[6]
        ymax=splitannotation[7]


        if CROPBBOXTOIMAGE:
            xmin = float(max(0,int(xmin)))
            ymin = float(max(0,int(ymin)))
            xmax = float(min(imsize[1]-1,int(xmax)))
            ymax = float(min(imsize[0]-1,int(ymax)))

            assert(xmin>=0)
            assert(ymin>=0)
            assert(xmax<=imsize[1])
            assert(ymax<=imsize[0])


        (x,y,width,height) = convert(imsize,(xmin,xmax,ymin,ymax))

        yoloannotationlist.append([objectclass,x,y,width,height])

    return yoloannotationlist






def convertAnnotationFile2VOC(annotationFile,exportdir):
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = "VOC2007"

    with open(annotationFile,'r') as f:
        KittiAnnotations = f.readlines()

    tree = kitti2voc(KittiAnnotations)

    filename = os.path.basename(annotationFile)
    savedir = os.path.join(exportdir,filename.replace('txt','xml'))
    tree.write(savedir, encoding="UTF-8")


def convertAnnotationFile2YOLO(annotationFile,exportdir):
    with open(annotationFile,'r') as f:
        KittiAnnotations = f.readlines()

    yoloannotationlist = kitti2yolo(KittiAnnotations)

    filename = os.path.basename(annotationFile)
    savedir = os.path.join(exportdir,filename)
    with open(savedir,'w') as fid:
        fid.writelines(yoloannotationlist)
