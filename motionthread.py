# -*- coding: UTF-8 -*-
"""
FileName: motioncthread.py
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
import systempath
import sys
import log
from imp import reload

sys.path.append(systempath.bundle_dir + '/Scripts')
try:
    import automationscript
except Exception as e:
    log.loginfo.process_log(e)

def reload_scripts():
    try:
        reload(automationscript)
        log.loginfo.process_log('reload auto script ok')
    except Exception as e:
        log.loginfo.process_log(e)


auto = None
class Motion(QtCore.QThread):
    iosingnal = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(Motion, self).__init__(parent)
        self.io_name = []
        self.io_desc = []
        self.io_value = []
        self.io_index = []
        self.writing = False
        global auto
        auto = automationscript.AutoMation()

    def read_io_config(self):
        self.path = systempath.bundle_dir + '/CSV Files/' + 'IO Config.csv'
        csvfile = open(self.path, 'r')
        reader = csv.reader(csvfile)
        self.io_name = []
        self.io_desc = []
        self.io_index = []
        i = 0
        for seq in reader:
            self.io_name.append(seq[0])
            self.io_desc.append(seq[1])
            if(i!=0):
                self.io_index.append(int(seq[2]))
            i = i + 1

    def read_axis_config(self):
        self.path = systempath.bundle_dir + '/CSV Files/' + 'Axis Config.csv'
        csvfile = open(self.path, 'r')
        reader = csv.reader(csvfile)
        self.axis_name = []
        self.axis_desc = []
        for seq in reader:
            self.axis_name.append(seq[0])
            self.axis_desc.append(seq[1])

    def initialize_motion(self):
        # 创建连接
        if(auto.create_connect()):
            log.loginfo.process_log('Connect PLC OK!')
        else:
            log.loginfo.process_log('Connect PLC Fail!')
        self.recv_thread = threading.Thread(target=self.refresh_rt_info)
        self.recv_thread.setDaemon(True)
        self.recv_thread.start()

    def write_io(self, index, value):
        self.writing = True
        m_index = self.io_index[index]
        ret = auto.write_io_state(m_index, value)
        self.writing = False
        if(ret == False):
            log.loginfo.process_log('Write IO fail!')

    def read_io_state(self):
        ret = auto.read_io_state()
        self.io_value = []
        for index in self.io_index:
            self.io_value.append(ret[index-min(self.io_index)])
        return self.io_value

    def refresh_rt_info(self):
        while(True):
            if(self.writing == False):
                self.iosingnal.emit([auto.read_rt_pos(), self.read_io_state()])
                time.sleep(0.05)