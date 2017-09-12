# -*- coding: UTF-8 -*-
"""
FileName: automationscript.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 自动化脚本，将运动控制相关函数定义在改文件
Update date：2017.7.20
version 1.0.0
"""

import random
import socket
import struct
import time
import systempath
import csv
import serial
import os

class AutoMation():
    def __init__(self):
        self.io = self.read_config()

    #读取IO配置列表
    def read_config(self):
        self.path = os.getcwd()
        self.cvspath = systempath.bundle_dir+ '/CSV Files/' + 'IO Config.csv'
        csvfile = open(self.cvspath, 'r')
        reader = csv.reader(csvfile)
        self.io_channel=[]
        self.io_channel2=[]
        for seg in reader:
            self.io_channel.append(seg[2])
        for seg2 in self.io_channel[1:]:    #从csv表第2行开始读int数据
            self.io_channel2.append(int(seg2))
        self.io_channel2 = sorted(self.io_channel2)
        self.start_index = self.io_channel2[0]      #io开始位索引
        self.io_length = self.io_channel2[-1]-self.io_channel2[0]+1     #读取长度
        return [self.start_index, self.io_length]

    def create_connect(self):
        return True

    def close_connect(self):
        self.com.close()

    def choose_axis(self, axis_name):
        time.sleep(0.1)

    def read_rt_pos(self):
        return 1

    def jog_forward(self):
        return True

    def jog_backward(self):
        return True

    def absolute_run(self, value):
        return True

    def relative_run(self, value):
        return True

    def go_home(self):
        return True

    def reset(self):
        return True

    def stop(self):
        return True

    def read_io_state(self):
        io_state = '0'
        io_state = io_state.zfill(self.io[1])
        return io_state

    def write_io_state(self,index,value):
        return True