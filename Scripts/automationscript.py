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

class AutoMation():
    def read_rt_pos(self):
        return random.random()

    def jog_forward(self):
        return True

    def jog_backward(self):
        return True

    def absolute_run(self, d):
        return True

    def relative_run(self, d):
        return True

    def read_io_state(self, num):
        return 1
    