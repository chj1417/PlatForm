# -*- coding: UTF-8 -*-
"""
FileName: log.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 加载CSV，初始化logger，写log
Update date：2017.7.20
version 1.0.0
"""

import logging.handlers
import time
import csv
import sys
import os
import inihelper
from PyQt5.QtWidgets import *
import systempath

date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
curpath = systempath.bundle_dir
LOG_FILE = curpath + '/Log/' + date+'.log'

# 创建一个logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

stationnum = '1'
class Load(QMainWindow):
    def __init__(self, path, parent=None):
        global curpath
        self.path = curpath + '/CSV Files/' + path
        self.seq_col1 = []
        self.seq_col2 = []
        self.seq_col3 = []
        self.seq_col4 = []
        self.seq_col5 = []
        self.seq_col6 = []
        self.seq_col7 = []
        self.testitems = []
    def load_seq(self):
        self.seq_col1 = []
        self.seq_col2 = []
        self.seq_col3 = []
        self.seq_col4 = []
        self.seq_col5 = []
        self.seq_col6 = []
        self.seq_col7 = []
        self.testitems = []
        #除第一次加载外，其他时候的加载都会弹出文件选择对话框
        global stationnum, curpath
        stationnum = inihelper.read_ini('Config', 'Station')
        Load.firstload = False
        csvfile = open(self.path, 'r')
        reader = csv.reader(csvfile)
        for seq in reader:
            self.seq_col1.append(seq[0])
            self.seq_col3.append(seq[2])
            self.seq_col4.append(seq[3])
            self.seq_col5.append(seq[4])
            self.seq_col6.append(seq[5])
            self.seq_col7.append(seq[6])
            self.seq_col2.append(seq[1])

    def load_seq_from_file(self):
        #除第一次加载外，其他时候的加载都会弹出文件选择对话框
        dir_path = QFileDialog.getOpenFileName(None, "choose directory", "", "Csv files(*.csv)")
        if(dir_path[0] != ''):
            csvfile = open(dir_path[0], 'r')
            reader = csv.reader(csvfile)
            self.seq_col1 = []
            self.seq_col2 = []
            self.seq_col3 = []
            self.seq_col4 = []
            self.seq_col5 = []
            self.seq_col6 = []
            self.seq_col7 = []

        for seq in reader:
            self.seq_col1.append(seq[0])
            self.seq_col2.append(seq[1])
            self.seq_col3.append(seq[2])
            self.seq_col4.append(seq[3])
            self.seq_col5.append(seq[4])
            self.seq_col6.append(seq[5])
            self.seq_col7.append(seq[6])

    def write_csv(self, data, seqnum):
        global curpath
        st = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        filepath = curpath + '/Result/' + st + '_sequence' + str(seqnum) + '.csv'
        if (not os.path.exists(filepath)):
            f = open(filepath, 'a+')  # 采用b的方式处理可以省去很多问题
            writer = csv.writer(f)
            datalog1 = ['SN', 'Pass/Fail', 'errStr', 'StartTime', 'EndTime', 'TestTime']
            datalog1.extend(self.seq_col1[1:len(self.seq_col1)])
            datalog2 = ['Function', '', '', '', '', '']
            datalog2.extend(self.seq_col2[1:len(self.seq_col2)])
            datalog3 = ['Mode', '', '', '', '', '']
            datalog3.extend(self.seq_col3[1:len(self.seq_col3)])
            datalog4 = ['Lower Limit', '', '', '', '', '']
            datalog4.extend(self.seq_col4[1:len(self.seq_col4)])
            datalog5 = ['Upper Limit', '', '', '', '', '']
            datalog5.extend(self.seq_col5[1:len(self.seq_col5)])
            writer.writerow(datalog1)
            writer.writerow(datalog2)
            writer.writerow(datalog3)
            writer.writerow(datalog4)
            writer.writerow(datalog5)
            f.close()
        f = open(filepath, 'a+')  # 采用b的方式处理可以省去很多问题
        writer = csv.writer(f)
        writer.writerow(data)









