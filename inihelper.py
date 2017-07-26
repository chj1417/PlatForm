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
import load
import systempath
import log

def read_ini(section, key):
    cf = configparser.ConfigParser()
    cf.read(systempath.bundle_dir + '/Config/Config.ini')
    value = cf.get(section, key)
    return value

def write_ini(section, key, value):
    cf = configparser.ConfigParser()
    cf.set(section, key, value)
    # write to file
    cf.write(open(systempath.bundle_dir + '/Config/Config.ini', "w"))
