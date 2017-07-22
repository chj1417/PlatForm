# -*- coding: UTF-8 -*-
"""
FileName: login.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 用户登陆
Update date：2017.7.20
version 1.0.0
"""

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from loginwindow import *
from log import *

class UserManager(Ui_login,QDialog):
    loginsignal = QtCore.pyqtSignal(list)
    loginok = True
    username = ''
    def __init__(self, parent=None):
        super(UserManager, self).__init__(parent)
        self.setupUi(self)
        self.cb_user.currentIndexChanged.connect(self.userchange)
        self.pb_login.clicked.connect(self.userlogin)
        self.pb_exit.clicked.connect(self.exit)
        self.screen = QDesktopWidget().screenGeometry()
        self.width = self.screen.width()
        self.height = self.screen.height()
        self.setFixedSize(self.width*0.3,self.height * 0.28)
        self.lb_login.setMaximumHeight(self.height * 0.16)
        self.lb_login.setMaximumWidth(self.width * 0.3)
        self.lb_image.setMaximumHeight(self.height * 0.08)
        self.lb_layout.setMaximumHeight(self.height * 0.03)
        self.lb_image.setMaximumWidth(self.width * 0.06)
        self.pb_login.setMaximumWidth(self.width * 0.1)
        self.pb_exit.setMaximumWidth(self.width * 0.1)
        self.le_pwd.setFocus()
        pixMap = QPixmap(curpath + '/Resource/user.png')
        self.lb_image.setPixmap(pixMap)

    def exit(self):
        UserManager.loginok = False
        self.accept()

    def closeEvent(self, event):
        UserManager.loginok = False
        self.accept()

    def userchange(self):
        if(self.cb_user.currentIndex()==0):
            self.lb_pwd.setText('PassWord:')
            self.le_pwd.setEchoMode(2)
        else:
            self.lb_pwd.setText('OperatorID:')
            self.le_pwd.setEchoMode(0)

    def userlogin(self):
        if((self.cb_user.currentIndex()==0) and (self.le_pwd.text() == '1')):
            logger.info('Administrator login')
            UserManager.username = 'Administrator'
            self.loginsignal.emit(['Administrator'])
            UserManager.loginok = True
            self.accept()
        elif(self.cb_user.currentIndex() == 1):
            if(self.le_pwd.text() == ''):
                QMessageBox.information(self, ("Warning!"), ("Invalid operator!"),
                                        QMessageBox.StandardButton(QMessageBox.Ok))
            else:
                logger.info('Operator ' + self.le_pwd.text() + ' login')
                UserManager.username = self.le_pwd.text()
                self.loginsignal.emit([self.le_pwd.text()])
            UserManager.loginok = True
            self.accept()
        else:
            # 除了information还有warning、about等
            QMessageBox.information(self, ("Warning!"), ("Password Error!"), QMessageBox.StandardButton(QMessageBox.Ok))
            logger.info('error password')



