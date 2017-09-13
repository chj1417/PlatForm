# -*- coding: UTF-8 -*-
"""
FileName: visionscript.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 视觉脚本
Update date：2017.7.20
version 1.0.0
"""


import systempath
import time


class Vision():
    def __init__(self):
        self.cap = None
        #self.dll = CDLL(systempath.bundle_dir + '/Refrence/libPythonSo.dylib')

    def init_window(self,id,row1,col1,row2,col2):
        self.dll.initialize_window(c_int(id), row1, col1, row2, col2)

    def load_image(self):
        img = cv.imread('test.bmp', cv.IMREAD_GRAYSCALE)  # IMREAD_GRAYSCALE   IMREAD_COLOR
        qimg = self.convert_to_qimage(img)
        return qimg

    def convert_to_qimage(self, im, copy=False):
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()

        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                    return qim.copy() if copy else qim

    def find_cameras(self, dev):
        cams = []
        type = c_char_p(dev)
        device = self.dll.find_camera
        device.restype = c_char_p
        try:
            device = self.dll.find_camera(type, 0)
            cam = device.decode()
            if(cam!=''):
                cams.append(cam)
        except Exception as e:
            print(e)
        return cams

    def open_camera(self, num):
        try:
            self.dll.open_camera(num)
        except Exception as e:
            print(e)
        return True

    def close_camera(self):
        try:
            self.dll.close_camera()
        except Exception as e:
            print(e)

    def snap(self):
        self.dll.capture_image(False)