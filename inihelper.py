# -*- coding: UTF-8 -*-
"""
FileName: inihelper.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 读写ini文件
Update date：2017.7.20
version 1.0.0
"""

import configparser
import sys
import os
import log

def read_ini(section, key):
    cf = configparser.ConfigParser()
    cf.read(log.curpath + '/Config/Config.ini')
    value = cf.get(section, key)
    return value

def write_ini(section, key, value):
    curpath = sys.path[0]
    cf = configparser.ConfigParser()
    cf.set(section, key, value)
    # write to file
    cf.write(open(curpath + '/Config/Config.ini', "w"))
