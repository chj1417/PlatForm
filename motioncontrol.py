# -*- coding: UTF-8 -*-
"""
FileName: motioncontrol.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 运动控制相关操作
Update date：2017.7.20
version 1.0.0
"""

import csv
import sys
import random
import time
import threading
from PyQt5 import QtCore
from Scripts.automationscript import *
import systempath
import sys
import log


class Motion(QtCore.QThread):
    iosingnal = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(Motion, self).__init__(parent)
        self.io_name = []
        self.io_desc = []
        self.auto = AutoMation()
        self.io_state = [0,0,0,1,1,1,0,1,1,0]

    def read_motion_config(self):
        self.path = systempath.bundle_dir + '/CSV Files/' + 'IO Config.csv'
        csvfile = open(self.path, 'r')
        reader = csv.reader(csvfile)
        self.io_name = []
        self.io_desc = []
        for seq in reader:
            self.io_name.append(seq[0])
            self.io_desc.append(seq[1])
        self.recv_thread = threading.Thread(target=self.refresh_rt_info)
        self.recv_thread.setDaemon(True)
        self.recv_thread.start()

    def refresh_rt_info(self):
        while(True):
            self.iosingnal.emit([self.auto.read_rt_pos(), self.io_state])
            time.sleep(0.1)