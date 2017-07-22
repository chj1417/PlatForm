# -*- coding: UTF-8 -*-
"""
FileName: zmqserver.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: zmq Server
Update date：2017.7.20
version 1.0.0
"""

import time
import zmq
from PyQt5 import QtCore

# zmq线程类
class ZmqComm(QtCore.QThread):
    # 构造函数里增加形参
    zmqrecvsingnal = QtCore.pyqtSignal(list)
    zmqsendsingnal = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super(ZmqComm, self).__init__(parent)
        self.message = ''

    def zmq_server(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        print('ZMQ Server Start...')
        self.zmqrecvsingnal.emit(['ServerStart'])
        while True:
            self.message = socket.recv_string()
            self.zmqrecvsingnal.emit([self.message])
            time.sleep(0.01)
            msg = "Server RecvOK!"
            socket.send_string(msg)
            self.zmqsendsingnal.emit([msg])
        self.zmqrecvsingnal.emit(['ServerStop'])

    # 重写 run() 函数，在该线程中执行测试函数
    def run(self):
        self.zmq_server()