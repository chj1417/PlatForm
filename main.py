# -*- coding: UTF-8 -*-
"""
FileName: main.py
Author: jiaminbit@sina.com
Create date: 2017.6.20
description: 主程序
Update date：2017.7.20
version 1.0.0
"""

from login import *
import systempath
import sys
import csv
import load
import log
import os
import inihelper
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction
from mainwindow import *
from tcptool import *
from zmqtool import *
from serialtool import *
from motioncontrol import *
import testthread
import zmqserver


class TestSeq(Ui_MainWindow,QMainWindow):
    def __init__(self, parent=None):
        super(TestSeq, self).__init__(parent)
        self.screen = QDesktopWidget().screenGeometry()
        self.width = self.screen.width()
        self.height = self.screen.height()
        # 两个树形控件的root items
        self.root1 = []
        self.root2 = []
        self.load1 = load.Load('Seq.csv')
        self.load2 = load.Load('Seq2.csv')
        self.bwThread1 = testthread.TestThread(self.load1, 1)
        self.bwThread2 = testthread.TestThread(self.load2, 2)
        self.setupUi(self)

        self.btn_stop.clicked.connect(self.test_break)
        self.btn_start.clicked.connect(self.test_start)
        self.btn_saveseq.clicked.connect(self.save_sequence)
        self.actionReload_CSV.triggered.connect(self.load_sequence)
        self.actionEdit_Sequence.triggered.connect(self.edit_sequence)
        self.cb_seq.currentIndexChanged.connect(self.edit_sequence)

        # 菜单项槽函数连接       ﻿
        self.actionReload_Scripts.triggered.connect(self.reload_scripts)

        self.actionLogin.triggered.connect(self.change_user)
        self.actionMain_Window.triggered.connect(self.switch_to_mainwindow)
        self.actionEdit_Window.triggered.connect(self.switch_to_editwindow)
        self.actionMotion_Debug.triggered.connect(self.motion_debug_tool)
        self.actionZmq_Debug.triggered.connect(self.zmq_debug_tool)
        self.actionTcp_Debug.triggered.connect(self.tcp_debug_tool)
        self.actionSerial_Debug.triggered.connect(self.serial_debug_tool)
        self.actionToolBar.triggered.connect(self.view_toolbar)

        log.loginfo = log.Log()
        self.load1.load_seq()
        self.load2.load_seq()
        log.loginfo.process_log('Load sequence')
        self.initialize_ui()
        self.initialize_seq()

        # 连接子进程的信号和槽函数
        self.bwThread1.finishSignal.connect(self.test_end)
        self.bwThread1.refresh.connect(self.refresh_ui)
        log.loginfo.refreshlog.connect(self.refresh_log)
        self.bwThread2.finishSignal.connect(self.test_end)
        self.bwThread2.refresh.connect(self.refresh_ui2)
        self.bwThread1.refreshloop.connect(self.loop_refresh)
        self.bwThread2.refreshloop.connect(self.loop_refresh)
        self.zmq = zmqserver.ZmqComm()
        self.zmq.zmqrecvsingnal.connect(self.recv_server)
        # 开启zmq server
        self.zmq.start()

        # 实例化登陆类
        global user
        user.loginsignal.connect(self.refresh_user)
        # 实例化tcp，zmq调试工具类
        self.tcptool = TcpTool()
        self.zmqtool = ZmqTool()
        # 连接zmq发送接收信号，显示信息到调试工具界面
        self.zmq.zmqrecvsingnal.connect(self.zmqtool.display_recv_msg)
        self.zmq.zmqsendsingnal.connect(self.zmqtool.display_send_msg)
        # 实例化手动控制类
        self.motion = Motion()
        self.motion.iosingnal.connect(self.refresh_motion_para)
        self.serialtool = SerialTool()

    # 初始化UI
    def initialize_ui(self):
        log.loginfo.process_log('Initialize UI')
        self.lb_title.setText(inihelper.read_ini('Config', 'Title'))
        self.lb_ver.setText(inihelper.read_ini('Config', 'Version'))
        self.tabWidget.tabBar().hide()
        self.tabWidget.setCurrentIndex(0)

        # 初始化统计信息显示区
        self.le_time.setText('0')
        self.le_pass.setText('0')
        self.le_total.setText('0')
        self.le_yield.setText('0')
        global pe, pe2
        pe = QPalette()
        self.lb_state.setAutoFillBackground(True)  # 设置背景充满，为设置背景颜色的必要条件
        self.lb_state2.setAutoFillBackground(True)
        self.lb_state.setText('Pass')
        pe.setColor(QPalette.Window, QColor(0, 255, 0))  # 设置背景颜色
        self.lb_state.setPalette(pe)  # 设置label背景色

        # 初始化用户名
        self.le_main_user.setText(UserManager.username)

        # 初始化各控件大小
        self.setMinimumHeight(self.height * 0.5)
        self.setMinimumWidth(self.width * 0.5)
        self.lb_title.setFixedHeight(self.height * 0.1)
        self.le_main_user.setMaximumWidth(self.width * 0.1)

        self.lb_ver.setMaximumHeight(self.height * 0.015)
        self.lb_ver.setMaximumWidth(self.width * 0.06)
        self.lb_zmqtitle.setMaximumWidth(self.width * 0.05)
        self.lb_zmqstate.setMaximumWidth(self.width * 0.01)
        self.lb_seqtitle.setMaximumWidth(self.width * 0.05)
        self.lb_seqstate.setMaximumWidth(self.width * 0.01)
        self.lb_seqstate.setStyleSheet('background-color: rgb(0, 237, 0);')
        # self.lb_zmqtitle.setMaximumHeight(self.height * 0.015)
        # self.lb_zmqtitle.setMaximumHeight(self.height * 0.015)
        # self.lb_seqtitle.setMaximumHeight(self.height * 0.015)
        # self.lb_seqtitle.setMaximumWidth(self.width * 0.5)


        self.te_log.setMaximumHeight(self.height * 0.1)
        self.testlist.setMaximumHeight(self.height * 0.6)
        self.testlist2.setMaximumHeight(self.height * 0.6)
        self.group1.setMaximumWidth(self.width * 0.1)
        self.group2.setMaximumWidth(self.width * 0.1)
        self.btn_group.setMaximumWidth(self.width * 0.1)
        self.group1.setMaximumHeight(self.height * 0.25)
        self.group2.setMaximumHeight(self.height * 0.25)
        self.btn_group.setMaximumHeight(self.height * 0.1)
        # self.cb_zero.setChecked(False)

        # 初始化工具栏
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(systempath.bundle_dir + "/Resource/start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(systempath.bundle_dir + "/Resource/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(systempath.bundle_dir + "/Resource/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(systempath.bundle_dir + "/Resource/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStart.setIcon(icon1)
        self.actionStop.setIcon(icon2)
        self.actionMainwindow.setIcon(icon3)
        self.actionRefresh.setIcon(icon4)
        self.actionStart.triggered.connect(self.test_start)
        self.actionStop.triggered.connect(self.test_break)
        self.actionPause.triggered.connect(self.test_pause)
        self.actionContinue.triggered.connect(self.continue_tool)
        self.actionLoginTool.triggered.connect(self.change_user)
        self.actionEdit.triggered.connect(self.edit_sequence)
        self.actionAutomation.triggered.connect(self.motion_debug_tool)
        self.actionMainwindow.triggered.connect(self.switch_to_mainwindow)
        self.actionRefresh.triggered.connect(self.reload_scripts)

        font = QtGui.QFont()
        font.setPointSize(10)
        self.mystepbar = QCheckBox()
        self.mystepbar.setText('StepTest')
        self.mystepbar.setToolTip('Enable step test')
        self.mystepbar.setFont(font)
        self.toolBar.addWidget(self.mystepbar)
        self.nextAction = QAction('Next', self)
        self.toolBar.addAction(self.nextAction)
        self.nextAction.triggered.connect(self.next_step)
        self.nextAction.setToolTip('Next step')
        self.nextAction.setDisabled(True)
        self.toolBar.addSeparator()

        self.myloopbar = QCheckBox()
        self.myloopbar.setText('LoopTest')
        self.myloopbar.setToolTip('Enable loop test')
        self.toolBar.addWidget(self.myloopbar)
        self.myeditbar = QLineEdit()
        self.myeditbar.setText('0')
        self.myeditbar.setToolTip('Loop test times')
        self.myloopbar.setFont(font)
        self.myeditbar.setMaximumWidth(self.width * 0.03)
        self.myeditbar.setStyleSheet('background-color: rgb(237, 237, 237);')
        self.myeditbar.setFont(font)
        self.toolBar.addWidget(self.myeditbar)
        self.toolBar.addSeparator()
        self.actionContinue.setDisabled(True)

        # 连接工具栏事件槽函数
        self.myloopbar.clicked.connect(self.enable_loop)
        self.myeditbar.textEdited.connect(self.edit_looptime)
        self.mystepbar.clicked.connect(self.step_test)

        if(log.stationnum == '2'):
            self.group2.setVisible(True)
            self.pbar2.setVisible(True)
            self.testlist2.setVisible(True)
            self.le_time2.setText('0')
            self.le_pass2.setText('0')
            self.le_total2.setText('0')
            self.le_yield2.setText('0')
            pe2 = QPalette()
            self.lb_state2.setText('Pass')
            pe2.setColor(QPalette.Window, QColor(0, 255, 0))  # 设置背景颜色
            self.lb_state2.setPalette(pe2)  # 设置label背景色
            self.root1 = self.initialize_tree(self.testlist, self.load1.seq_col1, self.load1.seq_col7)
            self.root2 = self.initialize_tree(self.testlist2, self.load2.seq_col1, self.load2.seq_col7)
            self.pbar.setRange(0, len(self.root1) - 1)
            self.pbar2.setRange(0, len(self.root2) - 1)
        else:
            self.group2.setVisible(False)
            self.pbar2.setVisible(False)
            self.testlist2.setVisible(False)
            self.root1 = self.initialize_tree(self.testlist, self.load1.seq_col1, self.load1.seq_col7)
            self.pbar.setRange(0, len(self.root1) - 1)

    # 初始化显示测试信息的树形结构
    def initialize_tree(self, tree, items, levels):
        log.loginfo.process_log('Initialize sequence tree')
        tree.setColumnCount(4)
        tree.setHeaderLabels(['TestItems', 'Test Time', 'TestData', 'TestResult'])
        tree.header().setSectionResizeMode(QHeaderView.Stretch)
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # 设置行高为25
        tree.setStyleSheet("QTreeWidget::item{height:%dpx}"%int(self.height*0.03))
        j = 0
        root = []
        for seq in items[1:len(items)]:
            if(levels[j+1] == 'root'):
                root0 = QTreeWidgetItem(tree)
                root.append(root0)
            # 设置根节点的名称
                root0.setText(0, seq)
            else:
                child = QTreeWidgetItem(root0)
                child.setText(0, seq)
            j = j + 1
        return root

    # 初始化编辑测试序列的表格
    def initialize_seq(self):
        log.loginfo.process_log('Initialize edit sequence')
        self.tableseq.setRowCount(50)
        self.tableseq.setColumnCount(7)
        self.tableseq.setColumnWidth(0, self.width*0.4)
        self.tableseq.setColumnWidth(1, self.width*0.2)
        self.tableseq.horizontalHeader().setStretchLastSection(True)
        self.btn_saveseq.setMaximumWidth(self.width*0.1)
        self.cb_seq.setMaximumWidth(self.width*0.1)

    # 重新加载Sequence
    def load_sequence(self):
        log.loginfo.process_log('Reload sequence')
        self.load1.load_seq()
        self.testlist.clear()
        self.root1 = self.initialize_tree(self.testlist, self.load1.seq_col1, self.load1.seq_col7)
        if (log.stationnum == '2'):
            self.load2.load_seq()
            self.testlist2.clear()
            self.root2 = self.initialize_tree(self.testlist2, self.load2.seq_col1, self.load2.seq_col7)

    def reload_scripts(self):
        log.loginfo.process_log('Reload scripts')
        testthread.reload_scripts()

    # 循环测试时刷新UI
    def loop_refresh(self, times):
        if (self.bwThread1.seq_end):
            if(self.bwThread1.looptime != 0):                     # 确保最后一次只更新循环次数
                self.clear_seq(self.root1, self.pbar)
                self.lb_state.setText('Testing...')
                pe.setColor(QPalette.Window, QColor(255, 255, 0))  # 设置背景颜色
                self.lb_state.setPalette(pe)  # 设置label背景色
            if (log.stationnum == '2'):
                self.myeditbar.setText(str(self.bwThread1.looptime) + '  ' + str(self.bwThread2.looptime))
            else:
                self.myeditbar.setText(str(self.bwThread1.looptime))

            # 单工位时不运行
        if (log.stationnum == '2'):
            if (self.bwThread2.seq_end):
                if(self.bwThread2.looptime != 0):                 # 确保最后一次只更新循环次数
                    self.clear_seq(self.root2, self.pbar2)
                    self.lb_state2.setText('Testing...')
                    pe2.setColor(QPalette.Window, QColor(255, 255, 0))  # 设置背景颜色
                    self.lb_state2.setPalette(pe2)  # 设置label背景色
                self.myeditbar.setText(str(self.bwThread1.looptime) + '  ' + str(self.bwThread2.looptime))

    # 开始测试
    def test_start(self):
        log.loginfo.process_log('Start test')
        self.bwThread1.stop = False
        self.bwThread2.stop = False
        self.btn_start.setDisabled(True)
        self.actionStart.setDisabled(True)
        # 开始执行 run() 函数里的内容,只有测试结束了的线程才能开始
        if(self.bwThread1.seq_end):
            self.clear_seq(self.root1,self.pbar)
            self.bwThread1.start()
            self.lb_state.setText('Testing...')
            pe.setColor(QPalette.Window, QColor(255, 255, 0))  # 设置背景颜色
            self.lb_state.setPalette(pe)  # 设置label背景色
        # 单工位时不运行
        if (log.stationnum == '2'):
            if (self.bwThread2.seq_end):
                self.clear_seq(self.root2, self.pbar2)
                self.bwThread2.start()
                self.lb_state2.setText('Testing...')
                pe2.setColor(QPalette.Window, QColor(255, 255, 0))  # 设置背景颜色
                self.lb_state2.setPalette(pe2)  # 设置label背景色

    # 测试结束后刷新UI等
    def test_end(self, ls):
        # 使用传回的返回值
        if (ls[2] == 1):
            self.le_time.setText(str(round(ls[0], 2)) + 's')
            self.btn_start.setDisabled(False)
            self.actionStart.setDisabled(False)
            self.le_total.setText(str(int(self.le_total.text()) + 1))
            self.lb_state.setText(ls[1])
            if ls[1] == 'Pass':
                self.le_pass.setText(str(int(self.le_pass.text()) + 1))
                # self.lb_state.setText('Pass')
                pe.setColor(QPalette.Window, QColor(0, 255, 0))  # 设置背景颜色
                self.lb_state.setPalette(pe)  # 设置label背景色
            else:
                # self.lb_state.setText('Fail')
                pe.setColor(QPalette.Window, QColor(255, 0, 0))  # 设置背景颜色
                self.lb_state.setPalette(pe)  # 设置label背景色
            y = int(self.le_pass.text()) / int(self.le_total.text())
            self.le_yield.setText(str("%.2f" % (y * 100)) + '%')
        else:
            self.le_time2.setText(str(round(ls[0], 2)) + 's')
            self.btn_start.setDisabled(False)
            self.actionStart.setDisabled(False)
            self.le_total2.setText(str(int(self.le_total2.text()) + 1))
            if ls[1] == 'Pass':
                self.le_pass2.setText(str(int(self.le_pass2.text()) + 1))
                self.lb_state2.setText('Pass')
                pe2.setColor(QPalette.Window, QColor(0, 255, 0))  # 设置背景颜色
                self.lb_state2.setPalette(pe2)  # 设置label背景色
            else:
                self.lb_state2.setText('Fail')
                pe2.setColor(QPalette.Window, QColor(255, 0, 0))  # 设置背景颜色
                self.lb_state2.setPalette(pe2)  # 设置label背景色
            y = int(self.le_pass2.text()) / int(self.le_total2.text())
            self.le_yield2.setText(str("%.2f" % (y * 100)) + '%')

    # 中止测试
    def test_break(self):
        log.loginfo.process_log('Break test')
        self.bwThread1.stop = True
        self.bwThread2.stop = True
        self.lb_state.setText('Break')
        self.lb_state2.setText('Break')

    # 暂停测试
    def test_pause(self):
        log.loginfo.process_log('Pause test')
        self.bwThread1.pause = True
        self.bwThread2.pause = True
        self.actionPause.setDisabled(True)
        self.actionContinue.setDisabled(False)

    # 开启或关闭单步测试
    def step_test(self):
        log.loginfo.process_log('Step test')
        if(self.mystepbar.isChecked()):
            self.bwThread1.pause = True
            self.bwThread2.pause = True
            self.nextAction.setDisabled(False)
        else:
            self.bwThread1.pause = False
            self.bwThread2.pause = False
            self.nextAction.setDisabled(True)

    # 下一步测试
    def next_step(self):
        self.bwThread1.pause = False
        self.bwThread2.pause = False
        time.sleep(0.1)
        self.bwThread1.pause = True
        self.bwThread2.pause = True

    # 暂停后继续测试
    def continue_tool(self):
        self.bwThread1.pause = False
        self.bwThread2.pause = False
        self.actionPause.setDisabled(False)
        self.actionContinue.setDisabled(True)

    # 开启或关闭循环测试
    def enable_loop(self):
        if(self.myloopbar.isChecked()):
            self.bwThread1.loop = True
            self.bwThread2.loop = True
            self.bwThread1.looptime = int(self.myeditbar.text())
            self.bwThread2.looptime = int(self.myeditbar.text())
        else:
            self.bwThread1.loop = False
            self.bwThread2.loop = False

    # 修改循环测试次数
    def edit_looptime(self):
        try:
            self.bwThread1.looptime = int(self.myeditbar.text())
            self.bwThread2.looptime = int(self.myeditbar.text())
        except Exception as e:
            print(e)

    # 测试过程中刷新UI，线程1
    def refresh_ui(self,ls):
        if(len(ls[2]) != 1):
            for i in range(len(ls[2])):
                self.root1[ls[0]].child(i).setText(2, str(ls[2][i]))
                self.root1[ls[0]].child(i).setText(3, ls[3][i])

        for i in range(1, 4):
            if (i != 3):
                self.root1[ls[0]].setText(i, str(ls[i]))
            else:
                if('Fail' in ls[i]):
                    self.root1[ls[0]].setText(i, 'Fail')
                elif(ls[i][0]== 'Skip'):
                    self.root1[ls[0]].setText(i, 'Skip')
                else:
                    self.root1[ls[0]].setText(i, 'Pass')

        if ls[3] == "Testing":
            for i in range(0,4):
                self.root1[ls[0]].setBackground(i, QBrush(QColor(0,255,100)))
        elif "Fail" in ls[3]:
            self.pbar.setValue(ls[0])
            for i in range(0,4):
                self.root1[ls[0]].setBackground(i, QBrush(QColor(255,0,0)))
        elif ls[3] == 'Pause':
            self.pbar.setValue(ls[0])
            for i in range(0, 4):
                self.root1[ls[0]].setBackground(i, QBrush(QColor(255, 255, 0)))
        else:
            self.pbar.setValue(ls[0])
            for i in range(0,4):
                self.root1[ls[0]].setBackground(i, QBrush(QColor(255,255,255)))

    # 测试过程中刷新UI，线程2
    def refresh_ui2(self, ls):
        if (len(ls[2]) != 1):
            for i in range(len(ls[2])):
                self.root2[ls[0]].child(i).setText(2, str(ls[2][i]))
                self.root2[ls[0]].child(i).setText(3, ls[3][i])

        for i in range(1, 4):
            if (i != 3):
                self.root2[ls[0]].setText(i, str(ls[i]))
            else:
                if ('Fail' in ls[i]):
                    self.root2[ls[0]].setText(i, 'Fail')
                elif (ls[i][0] == 'Skip'):
                    self.root2[ls[0]].setText(i, 'Skip')
                else:
                    self.root2[ls[0]].setText(i, 'Pass')

        if ls[3] == "Testing":
            for i in range(0, 4):
                self.root2[ls[0]].setBackground(i, QBrush(QColor(0, 255, 100)))
        elif "Fail" in ls[3]:
            self.pbar2.setValue(ls[0])
            for i in range(0, 4):
                self.root2[ls[0]].setBackground(i, QBrush(QColor(255, 0, 0)))
        elif ls[3] == 'Pause':
            self.pbar2.setValue(ls[0])
            for i in range(0, 4):
                self.root2[ls[0]].setBackground(i, QBrush(QColor(255, 255, 0)))
        else:
            self.pbar2.setValue(ls[0])
            for i in range(0, 4):
                self.root2[ls[0]].setBackground(i, QBrush(QColor(255, 255, 255)))

    # 清除除了测试名称外测试树形结构的其他内容以及进度条
    def clear_seq(self, tree, bar):
        bar.setValue(0)
        for root in tree:
            for i in range(0, 4):
                if(i != 0):
                    root.setText(i, '')
                root.setBackground(i, QBrush(QColor(255, 255, 255)))
                for j in range(root.childCount()):
                    root.child(j).setText(2, '')
                    root.child(j).setText(3, '')

    # 切换到序列编辑页面，并且将Seq1的信息读取到表格
    def edit_sequence(self):
        self.tabWidget.setCurrentIndex(1)
        self.tableseq.clear()
        self.tableseq.setHorizontalHeaderLabels(['TestItem', 'Function', 'Mode', 'Low Limit', 'Up Limit', 'Next Step', 'Level'])
        if(self.cb_seq.currentIndex() == 0):
            items = [self.load1.seq_col1, self.load1.seq_col2, self.load1.seq_col3, self.load1.seq_col4,
                     self.load1.seq_col5, self.load1.seq_col6, self.load1.seq_col7]
        else:
            items = [self.load2.seq_col1, self.load2.seq_col2, self.load2.seq_col3, self.load2.seq_col4,
                     self.load2.seq_col5, self.load2.seq_col6, self.load2.seq_col7]
        for j in range(7):
            i = 0
            for seq in items[j][1:len(items[j])]:
                if(j==2):
                    self.MyCombo = QComboBox()
                    self.MyCombo.addItem("test")
                    self.MyCombo.addItem("skip")
                    self.tableseq.setCellWidget(i, j, self.MyCombo)
                    if(seq == 'test'):
                        self.MyCombo.setCurrentIndex(0)
                    else:
                        self.MyCombo.setCurrentIndex(1)
                elif(j==5):
                    self.MyCombo1 = QComboBox()
                    self.MyCombo1.addItem("continue")
                    self.MyCombo1.addItem("finish")
                    self.tableseq.setCellWidget(i, j, self.MyCombo1)
                    if (seq == 'continue'):
                        self.MyCombo1.setCurrentIndex(0)
                    else:
                        self.MyCombo1.setCurrentIndex(1)
                elif (j == 6):
                    self.MyCombo2 = QComboBox()
                    self.MyCombo2.addItem("root")
                    self.MyCombo2.addItem("child")
                    self.tableseq.setCellWidget(i, j, self.MyCombo2)
                    if (seq == 'root'):
                        self.MyCombo2.setCurrentIndex(0)
                    else:
                        self.MyCombo2.setCurrentIndex(1)
                else:
                    newItem1 = QTableWidgetItem(seq)
                    self.tableseq.setItem(i, j, newItem1)
                i = i + 1

    # 保存测试序列信息
    def save_sequence(self):
        if (self.cb_seq.currentIndex() == 0):
            filepath = systempath.bundle_dir + '/CSV Files/Seq.csv'
        else:
            filepath = systempath.bundle_dir + '/CSV Files/Seq2.csv'
        f = open(filepath, 'w')
        writer = csv.writer(f)
        writer.writerow(['TestItem', 'Function', 'Mode', 'Low Limit', 'Up Limit', 'Next Step', 'Level'])
        for i in range(50):
            row = []
            if (self.tableseq.item(i, 0) != None):
                for j in range(7):
                    if(j==2):
                        if(self.tableseq.cellWidget(i, j).currentIndex()==0):
                            row.append('test')
                        else:
                            row.append('skip')
                    elif(j==5):
                        if (self.tableseq.cellWidget(i, j).currentIndex() == 0):
                            row.append('continue')
                        else:
                            row.append('finish')
                    elif(j==6):
                        if (self.tableseq.cellWidget(i, j).currentIndex() == 0):
                            row.append('root')
                        else:
                            row.append('child')
                    else:
                        row.append(self.tableseq.item(i,j).text())
                writer.writerow(row)
        f.close()
        self.load_sequence()

    # 切换到主界面
    def switch_to_mainwindow(self):
        self.tabWidget.setCurrentIndex(0)

    # 切换到序列编辑页面
    def switch_to_editwindow(self):
        self.tabWidget.setCurrentIndex(1)

    # 切换用户
    def change_user(self):
        global user
        user.show()

    # 刷新用户
    def refresh_user(self, ls):
        self.le_main_user.setText(ls[0])

    # 打开zmq调试工具
    def zmq_debug_tool(self):
        self.zmqtool.resize(self.width*0.5, self.height*0.5)
        self.zmqtool.lb_zmqtitle.setMaximumHeight(self.height*0.05)
        self.zmqtool.show()

    # 显示或隐藏toolbar
    def view_toolbar(self):
        if(self.actionToolBar.isChecked()):
            self.toolBar.setHidden(False)
        else:
            self.toolBar.setHidden(True)

    # 打开tcp调试工具
    def tcp_debug_tool(self):
        self.tcptool.resize(self.width*0.5, self.height*0.5)
        self.tcptool.lb_tcptitle.setMaximumHeight(self.height * 0.05)
        self.tcptool.show()

    # 打开串口调试工具
    def serial_debug_tool(self):
        self.serialtool.resize(self.width * 0.5, self.height * 0.5)
        self.serialtool.lb_serialtitle.setMaximumHeight(self.height * 0.05)
        self.serialtool.pb_serialsend.setMaximumWidth(self.width * 0.1)
        self.serialtool.pb_serialcon.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_serialname.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_baund.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_fluid.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_stopbit.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_checkbit.setMaximumWidth(self.width * 0.1)
        self.serialtool.cb_databit.setMaximumWidth(self.width * 0.1)
        self.serialtool.list_serial_port()
        self.serialtool.show()

    # 切换到手动控制界面
    def motion_debug_tool(self):
        self.motion.read_motion_config()
        self.initialize_io_table()
        self.tabWidget.setCurrentIndex(2)

    # 初始化IO表，从配置文件中读取信息
    def initialize_io_table(self):
        self.tw_io.setColumnCount(2)
        self.tw_io.setRowCount(len(self.motion.io_name) + 10)
        self.tw_io.setHorizontalHeaderLabels(['IO', 'Description'])
        self.lb_axis.setMaximumWidth(self.width*0.1)
        self.lb_axis.setMaximumHeight(self.height * 0.03)
        self.lb_io.setMaximumWidth(self.width * 0.1)
        self.lb_io.setMaximumHeight(self.height * 0.03)
        self.cb_axis.setMaximumWidth(self.width * 0.2)
        self.pb_jog1.setMaximumWidth(self.width*0.1)
        self.pb_jog2.setMaximumWidth(self.width * 0.1)
        self.pb_absolute.setMaximumWidth(self.width * 0.1)
        self.pb_relative.setMaximumWidth(self.width * 0.1)
        self.pb_stop.setMaximumWidth(self.width * 0.1)
        self.pb_reset.setMaximumWidth(self.width * 0.1)

        i = 0
        for seq in self.motion.io_name:
            if(i != 0):
                self.MyCheck = QCheckBox()
                self.MyCheck.setText('--- ' + seq)
                self.tw_io.setCellWidget(i-1, 0, self.MyCheck)
                newItem = QTableWidgetItem(self.motion.io_desc[i])
                self.tw_io.setItem(i - 1, 1, newItem)
            i = i+1
        self.tw_io.horizontalHeader().setStretchLastSection(True)

    # 刷新运动控制参数（IO）
    def refresh_motion_para(self,ls):
        self.dsb_real_pos.setValue(ls[0])
        i = 0
        for io in ls[1]:
            if(io == 1):
                self.tw_io.cellWidget(i, 0).setChecked(True)
            else:
                self.tw_io.cellWidget(i, 0).setChecked(False)
            i = i + 1

    # 解析zmq server收到的内容
    def recv_server(self, ls):
        if(ls[0] == 'Start'):
            self.test_start()
        if (ls[0] == 'ServerStart'):
            self.lb_zmqstate.setStyleSheet('background-color: rgb(0, 237, 0);')

    def refresh_log(self, msg):
        self.te_log.append(msg)

if __name__ == '__main__':
    '''
    主函数
    '''
    scriptpath = systempath.bundle_dir+'/Scripts/testscript.py'
    app = QApplication(sys.argv)
    if(not os.path.exists(scriptpath)):
        QMessageBox.information(None, ("Warning!"), ("Script Error!"), QMessageBox.StandardButton(QMessageBox.Ok))
    else:
        global user
        user = UserManager()
        user.show()
        # 等待对话框结束
        app.exec_()
        if(user.loginok):
            seq = TestSeq()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("Resource/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            seq.setWindowIcon(icon)
            seq.showMaximized()
            sys.exit(app.exec_())