#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mads Dyrmann
"""


#import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import os
import struct, imghdr, re

executor = ThreadPoolExecutor(max_workers=30)

CROPBBOXTOIMAGE = True


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


#        x = xmin
#        y = ymin
#        width = xmax-xmin
#        height = ymax-ymin
#
#        # Normalize to image size
#        x = 1.0*x/imsize[1]
#        width = 1.0*width/imsize[1]
#        y = 1.0*y/imsize[0]
#        height =1.0*height/imsize[0]

        yoloannotationlist.append([objectclass,x,y,width,height])

    return yoloannotationlist



def convertAnnotationFile(annotationFile,exportdir):
    with open(annotationFile,'r') as f:
        KittiAnnotations = f.readlines()

    yoloannotationlist = kitti2yolo(KittiAnnotations)

    filename = os.path.basename(annotationFile)
    savedir = os.path.join(exportdir,filename)
    with open(savedir,'w') as fid:
        fid.writelines(yoloannotationlist)


def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(32)
        if len(head) != 32:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        elif imghdr.what(fname) == 'pgm':
            header, width, height, maxval = re.search(
                b"(^P5\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", head).groups()
            width = int(width)
            height = int(height)
        elif imghdr.what(fname) == 'bmp':
            _, width, height, depth = re.search(
                b"((\d+)\sx\s"
                b"(\d+)\sx\s"
                b"(\d+))", str).groups()
            width = int(width)
            height = int(height)
        else:
            return
        return height, width

